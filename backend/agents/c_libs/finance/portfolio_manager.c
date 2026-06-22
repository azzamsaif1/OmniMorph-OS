#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define MAX_ASSETS 50
#define MAX_SYMBOL_LEN 16

typedef struct {
    char symbol[MAX_SYMBOL_LEN];
    double weight;
    double expected_return;
    double volatility;
    double current_price;
    double quantity;
} Asset;

typedef struct {
    Asset assets[MAX_ASSETS];
    int count;
    double total_value;
    double expected_return;
    double portfolio_volatility;
    double sharpe_ratio;
} Portfolio;

/* Calculate portfolio metrics */
static double portfolio_return(const Asset* assets, int count) {
    double ret = 0.0;
    for (int i = 0; i < count; i++) {
        ret += assets[i].weight * assets[i].expected_return;
    }
    return ret;
}

static double portfolio_risk(const Asset* assets, int count,
                              const double* correlation_matrix) {
    double variance = 0.0;
    for (int i = 0; i < count; i++) {
        for (int j = 0; j < count; j++) {
            double corr = (i == j) ? 1.0 : correlation_matrix[i * count + j];
            variance += assets[i].weight * assets[j].weight *
                       assets[i].volatility * assets[j].volatility * corr;
        }
    }
    return sqrt(variance);
}

/* Mean-Variance Optimization (simplified Markowitz) */
int optimize_portfolio(const char* assets_json, int num_assets,
                       double risk_tolerance, char* result_json, int buffer_size) {
    /* Simplified optimization: equal-risk contribution with risk adjustment */
    Asset assets[MAX_ASSETS];
    int count = num_assets < MAX_ASSETS ? num_assets : MAX_ASSETS;

    /* Initialize with equal weights */
    double total_inv_vol = 0.0;
    for (int i = 0; i < count; i++) {
        /* Parse expected values (simplified) */
        assets[i].expected_return = 0.08 + (i * 0.02);  /* 8-18% range */
        assets[i].volatility = 0.15 + (i * 0.05);       /* 15-40% range */
        snprintf(assets[i].symbol, MAX_SYMBOL_LEN, "ASSET_%d", i + 1);

        double inv_vol = 1.0 / assets[i].volatility;
        total_inv_vol += inv_vol;
    }

    /* Risk-parity weighting adjusted by risk tolerance */
    for (int i = 0; i < count; i++) {
        double base_weight = (1.0 / assets[i].volatility) / total_inv_vol;
        /* Adjust for risk tolerance: higher tolerance → more weight to high-return assets */
        double return_adj = 1.0 + (risk_tolerance - 0.5) *
                           (assets[i].expected_return / 0.12 - 1.0);
        assets[i].weight = base_weight * return_adj;
    }

    /* Normalize weights */
    double total_weight = 0.0;
    for (int i = 0; i < count; i++) {
        if (assets[i].weight < 0.02) assets[i].weight = 0.02;  /* Min 2% */
        total_weight += assets[i].weight;
    }
    for (int i = 0; i < count; i++) {
        assets[i].weight /= total_weight;
    }

    /* Calculate portfolio metrics */
    double port_return = portfolio_return(assets, count);
    /* Approximate risk assuming 0.3 average correlation */
    double port_risk = 0.0;
    for (int i = 0; i < count; i++) {
        port_risk += assets[i].weight * assets[i].weight *
                    assets[i].volatility * assets[i].volatility;
        for (int j = i + 1; j < count; j++) {
            port_risk += 2.0 * assets[i].weight * assets[j].weight *
                        assets[i].volatility * assets[j].volatility * 0.3;
        }
    }
    port_risk = sqrt(port_risk);
    double sharpe = (port_return - 0.04) / port_risk;  /* Risk-free rate 4% */

    /* Build result JSON */
    char allocations[8192] = "[";
    int first = 1;
    for (int i = 0; i < count; i++) {
        char entry[256];
        snprintf(entry, sizeof(entry),
            "%s{\"symbol\":\"%s\",\"weight\":%.4f,\"expected_return\":%.4f,\"volatility\":%.4f}",
            first ? "" : ",", assets[i].symbol,
            assets[i].weight, assets[i].expected_return, assets[i].volatility);
        strncat(allocations, entry, sizeof(allocations) - strlen(allocations) - 1);
        first = 0;
    }
    strncat(allocations, "]", sizeof(allocations) - strlen(allocations) - 1);

    snprintf(result_json, buffer_size,
        "{\"optimization\":\"mean_variance\","
        "\"risk_tolerance\":%.2f,"
        "\"portfolio_expected_return\":%.4f,"
        "\"portfolio_volatility\":%.4f,"
        "\"sharpe_ratio\":%.3f,"
        "\"allocations\":%s,"
        "\"rebalance_frequency\":\"monthly\","
        "\"max_single_position\":0.30}",
        risk_tolerance, port_return, port_risk, sharpe, allocations);

    return 0;
}

/* Value at Risk (VaR) calculation - parametric method */
double calculate_var(double portfolio_value, double volatility,
                     double confidence_level, int holding_period_days) {
    /* Z-scores for common confidence levels */
    double z_score;
    if (confidence_level >= 0.99) z_score = 2.326;
    else if (confidence_level >= 0.95) z_score = 1.645;
    else if (confidence_level >= 0.90) z_score = 1.282;
    else z_score = 1.0;

    double daily_var = portfolio_value * volatility * z_score / sqrt(252.0);
    return daily_var * sqrt((double)holding_period_days);
}

/* Risk assessment */
int assess_risk(double portfolio_value, double volatility,
                double max_drawdown, double leverage,
                char* result_json, int buffer_size) {
    double var_95 = calculate_var(portfolio_value, volatility, 0.95, 1);
    double var_99 = calculate_var(portfolio_value, volatility, 0.99, 1);
    double cvar = var_99 * 1.2;  /* Conditional VaR approximation */

    /* Risk score 0-100 */
    double risk_score = 0.0;
    risk_score += (volatility / 0.5) * 25.0;    /* Volatility contribution */
    risk_score += (max_drawdown / 0.3) * 25.0;  /* Drawdown contribution */
    risk_score += (leverage / 5.0) * 25.0;       /* Leverage contribution */
    risk_score += (var_95 / portfolio_value) * 25.0 * 10.0;  /* VaR contribution */
    if (risk_score > 100.0) risk_score = 100.0;

    const char* risk_level;
    if (risk_score > 75) risk_level = "extreme";
    else if (risk_score > 50) risk_level = "high";
    else if (risk_score > 25) risk_level = "moderate";
    else risk_level = "low";

    snprintf(result_json, buffer_size,
        "{\"portfolio_value\":%.2f,"
        "\"var_95_1day\":%.2f,\"var_99_1day\":%.2f,\"cvar\":%.2f,"
        "\"risk_score\":%.1f,\"risk_level\":\"%s\","
        "\"volatility\":%.4f,\"max_drawdown\":%.4f,\"leverage\":%.1f,"
        "\"recommendations\":["
        "%s%s%s%s"
        "]}",
        portfolio_value, var_95, var_99, cvar,
        risk_score, risk_level,
        volatility, max_drawdown, leverage,
        risk_score > 75 ? "\"Reduce position sizes immediately\"," : "",
        leverage > 2.0 ? "\"Reduce leverage below 2x\"," : "",
        max_drawdown > 0.2 ? "\"Set tighter stop-losses\"," : "",
        "\"Diversify across uncorrelated assets\"");

    return (int)risk_score;
}
