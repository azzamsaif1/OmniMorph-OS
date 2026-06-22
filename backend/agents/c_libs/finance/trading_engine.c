#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <time.h>

#define MAX_CANDLES 1000
#define MAX_SIGNALS 100
#define MAX_POSITIONS 50

typedef struct {
    double open;
    double high;
    double low;
    double close;
    double volume;
    long timestamp;
} Candle;

typedef struct {
    char symbol[16];
    char action[8];    /* "BUY" or "SELL" */
    double price;
    double confidence;
    char reason[256];
    long timestamp;
} Signal;

typedef struct {
    char symbol[16];
    char side[8];
    double entry_price;
    double current_price;
    double quantity;
    double pnl;
    double pnl_pct;
    long entry_time;
} Position;

/* Technical indicators */

static double calculate_sma(const double* prices, int count, int period) {
    if (count < period) return 0.0;
    double sum = 0.0;
    for (int i = count - period; i < count; i++) {
        sum += prices[i];
    }
    return sum / period;
}

static double calculate_ema(const double* prices, int count, int period) {
    if (count < period) return 0.0;
    double multiplier = 2.0 / (period + 1);
    double ema = prices[0];
    for (int i = 1; i < count; i++) {
        ema = (prices[i] - ema) * multiplier + ema;
    }
    return ema;
}

static double calculate_rsi(const double* prices, int count, int period) {
    if (count < period + 1) return 50.0;

    double gain_sum = 0.0, loss_sum = 0.0;
    for (int i = count - period; i < count; i++) {
        double change = prices[i] - prices[i - 1];
        if (change > 0) gain_sum += change;
        else loss_sum += (-change);
    }

    double avg_gain = gain_sum / period;
    double avg_loss = loss_sum / period;

    if (avg_loss == 0.0) return 100.0;
    double rs = avg_gain / avg_loss;
    return 100.0 - (100.0 / (1.0 + rs));
}

static void calculate_bollinger_bands(const double* prices, int count, int period,
                                       double* upper, double* middle, double* lower) {
    *middle = calculate_sma(prices, count, period);

    double variance = 0.0;
    for (int i = count - period; i < count; i++) {
        double diff = prices[i] - *middle;
        variance += diff * diff;
    }
    double std_dev = sqrt(variance / period);

    *upper = *middle + (2.0 * std_dev);
    *lower = *middle - (2.0 * std_dev);
}

static double calculate_macd(const double* prices, int count,
                              double* signal_line, double* histogram) {
    double ema12 = calculate_ema(prices, count, 12);
    double ema26 = calculate_ema(prices, count, 26);
    double macd = ema12 - ema26;

    /* Signal line is 9-period EMA of MACD (simplified) */
    *signal_line = macd * 0.8;  /* Approximation */
    *histogram = macd - *signal_line;
    return macd;
}

/* Generate trading signals from price data */
int generate_signals(const double* prices, int count, const char* symbol,
                     char* result_json, int buffer_size) {
    if (count < 26) {
        snprintf(result_json, buffer_size,
            "{\"error\":\"Insufficient data (need 26+ candles)\",\"signals\":[]}");
        return 0;
    }

    double sma20 = calculate_sma(prices, count, 20);
    double sma50 = calculate_sma(prices, count, 50 > count ? count : 50);
    double ema12 = calculate_ema(prices, count, 12);
    double ema26 = calculate_ema(prices, count, 26);
    double rsi = calculate_rsi(prices, count, 14);
    double bb_upper, bb_middle, bb_lower;
    calculate_bollinger_bands(prices, count, 20, &bb_upper, &bb_middle, &bb_lower);
    double macd_signal, macd_hist;
    double macd = calculate_macd(prices, count, &macd_signal, &macd_hist);

    double current = prices[count - 1];
    double prev = prices[count - 2];

    /* Determine signal */
    char action[8] = "HOLD";
    double confidence = 0.0;
    char reason[512] = "";

    int bullish_signals = 0;
    int bearish_signals = 0;

    /* RSI signals */
    if (rsi < 30) { bullish_signals += 2; }
    else if (rsi < 40) { bullish_signals += 1; }
    else if (rsi > 70) { bearish_signals += 2; }
    else if (rsi > 60) { bearish_signals += 1; }

    /* MACD crossover */
    if (macd > macd_signal && macd_hist > 0) { bullish_signals += 2; }
    else if (macd < macd_signal && macd_hist < 0) { bearish_signals += 2; }

    /* Bollinger Band signals */
    if (current < bb_lower) { bullish_signals += 2; }
    else if (current > bb_upper) { bearish_signals += 2; }

    /* SMA crossover */
    if (ema12 > ema26 && current > sma20) { bullish_signals += 1; }
    else if (ema12 < ema26 && current < sma20) { bearish_signals += 1; }

    /* Price momentum */
    if (current > prev && current > sma20) { bullish_signals += 1; }
    else if (current < prev && current < sma20) { bearish_signals += 1; }

    if (bullish_signals >= 4) {
        strcpy(action, "BUY");
        confidence = (double)bullish_signals / 8.0;
        snprintf(reason, sizeof(reason),
            "RSI=%.1f (oversold), MACD bullish crossover, price near lower BB", rsi);
    } else if (bearish_signals >= 4) {
        strcpy(action, "SELL");
        confidence = (double)bearish_signals / 8.0;
        snprintf(reason, sizeof(reason),
            "RSI=%.1f (overbought), MACD bearish crossover, price near upper BB", rsi);
    } else {
        strcpy(action, "HOLD");
        confidence = 0.5;
        snprintf(reason, sizeof(reason), "Mixed signals - no clear direction");
    }

    snprintf(result_json, buffer_size,
        "{\"symbol\":\"%s\",\"current_price\":%.4f,"
        "\"signal\":\"%s\",\"confidence\":%.2f,\"reason\":\"%s\","
        "\"indicators\":{"
        "\"rsi\":%.2f,\"sma20\":%.4f,\"sma50\":%.4f,"
        "\"ema12\":%.4f,\"ema26\":%.4f,"
        "\"macd\":%.4f,\"macd_signal\":%.4f,\"macd_histogram\":%.4f,"
        "\"bb_upper\":%.4f,\"bb_middle\":%.4f,\"bb_lower\":%.4f"
        "},\"bullish_count\":%d,\"bearish_count\":%d}",
        symbol, current, action, confidence, reason,
        rsi, sma20, sma50, ema12, ema26,
        macd, macd_signal, macd_hist,
        bb_upper, bb_middle, bb_lower,
        bullish_signals, bearish_signals);

    return (strcmp(action, "BUY") == 0) ? 1 : (strcmp(action, "SELL") == 0) ? -1 : 0;
}

/* Calculate position sizing using Kelly Criterion */
double kelly_position_size(double win_rate, double avg_win, double avg_loss,
                           double account_balance) {
    if (avg_loss == 0.0) return 0.0;
    double win_loss_ratio = avg_win / avg_loss;
    double kelly = win_rate - ((1.0 - win_rate) / win_loss_ratio);

    /* Use half-Kelly for safety */
    kelly *= 0.5;
    if (kelly < 0.0) kelly = 0.0;
    if (kelly > 0.25) kelly = 0.25;  /* Max 25% of account */

    return account_balance * kelly;
}

/* Backtest a strategy on historical data */
int backtest_strategy(const double* prices, int count, double initial_capital,
                      char* result_json, int buffer_size) {
    if (count < 50) {
        snprintf(result_json, buffer_size,
            "{\"error\":\"Need 50+ data points for backtest\"}");
        return -1;
    }

    double capital = initial_capital;
    double position = 0.0;
    int trades = 0, wins = 0, losses = 0;
    double max_drawdown = 0.0, peak = initial_capital;

    for (int i = 26; i < count - 1; i++) {
        double rsi = calculate_rsi(prices, i + 1, 14);
        double sma = calculate_sma(prices, i + 1, 20);

        if (position == 0.0 && rsi < 35 && prices[i] > sma) {
            /* Buy signal */
            position = capital * 0.95 / prices[i];
            capital -= position * prices[i];
            trades++;
        } else if (position > 0.0 && (rsi > 65 || prices[i] < sma * 0.95)) {
            /* Sell signal */
            double sell_value = position * prices[i];
            if (sell_value > (capital + position * prices[i - 1]) * 0.5) {
                wins++;
            } else {
                losses++;
            }
            capital += sell_value;
            position = 0.0;

            if (capital > peak) peak = capital;
            double dd = (peak - capital) / peak;
            if (dd > max_drawdown) max_drawdown = dd;
        }
    }

    /* Close any open position */
    if (position > 0.0) {
        capital += position * prices[count - 1];
        position = 0.0;
    }

    double total_return = ((capital - initial_capital) / initial_capital) * 100.0;
    double win_rate = trades > 0 ? (double)wins / trades * 100.0 : 0.0;

    snprintf(result_json, buffer_size,
        "{\"initial_capital\":%.2f,\"final_capital\":%.2f,"
        "\"total_return_pct\":%.2f,\"total_trades\":%d,"
        "\"wins\":%d,\"losses\":%d,\"win_rate\":%.1f,"
        "\"max_drawdown_pct\":%.2f,\"sharpe_estimate\":%.2f}",
        initial_capital, capital, total_return,
        trades, wins, losses, win_rate,
        max_drawdown * 100.0,
        total_return > 0 ? total_return / (max_drawdown * 100.0 + 1.0) : 0.0);

    return 0;
}
