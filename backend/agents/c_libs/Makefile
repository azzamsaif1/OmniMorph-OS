CC = gcc
CFLAGS = -Wall -Wextra -O2 -fPIC -shared
LDFLAGS = -lm

# Output directory
OUTDIR = lib

# Security libraries
SECURITY_SRCS = security/recon_agent.c security/vuln_analyzer.c security/exploit_agent.c
SECURITY_LIBS = $(OUTDIR)/librecon.so $(OUTDIR)/libvuln.so $(OUTDIR)/libexploit.so

# Finance libraries
FINANCE_SRCS = finance/trading_engine.c finance/portfolio_manager.c
FINANCE_LIBS = $(OUTDIR)/libtrading.so $(OUTDIR)/libportfolio.so

.PHONY: all clean security finance

all: $(OUTDIR) security finance

$(OUTDIR):
	mkdir -p $(OUTDIR)

# Security agents
security: $(OUTDIR) $(SECURITY_LIBS)

$(OUTDIR)/librecon.so: security/recon_agent.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

$(OUTDIR)/libvuln.so: security/vuln_analyzer.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

$(OUTDIR)/libexploit.so: security/exploit_agent.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

# Finance agents
finance: $(OUTDIR) $(FINANCE_LIBS)

$(OUTDIR)/libtrading.so: finance/trading_engine.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

$(OUTDIR)/libportfolio.so: finance/portfolio_manager.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -rf $(OUTDIR)
