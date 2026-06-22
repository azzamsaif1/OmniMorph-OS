#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_VULNS 256
#define MAX_CVE_LEN 20
#define MAX_DESC_LEN 512

typedef struct {
    char cve_id[MAX_CVE_LEN];
    char service[64];
    int port;
    float cvss_score;
    char severity[16];
    char description[MAX_DESC_LEN];
    int exploitable;
} Vulnerability;

typedef struct {
    int count;
    Vulnerability vulns[MAX_VULNS];
} VulnReport;

/* Known vulnerability database (embedded for offline operation) */
typedef struct {
    const char* service;
    const char* version_pattern;
    const char* cve_id;
    float cvss_score;
    const char* severity;
    const char* description;
    int exploitable;
} KnownVuln;

static const KnownVuln VULN_DB[] = {
    {"ssh", "OpenSSH_7", "CVE-2023-38408", 9.8, "critical",
     "Remote code execution in OpenSSH forwarded ssh-agent", 1},
    {"ssh", "OpenSSH_8.0", "CVE-2023-48795", 5.9, "medium",
     "Terrapin attack - prefix truncation in SSH", 0},
    {"http", "Apache/2.4.49", "CVE-2021-41773", 7.5, "high",
     "Path traversal and file disclosure in Apache HTTP Server", 1},
    {"http", "Apache/2.4.50", "CVE-2021-42013", 9.8, "critical",
     "Remote code execution via path traversal in Apache", 1},
    {"http", "nginx/1.18", "CVE-2021-23017", 7.7, "high",
     "DNS resolver vulnerability in nginx", 0},
    {"https", "OpenSSL/1.1.1", "CVE-2022-0778", 7.5, "high",
     "Infinite loop in BN_mod_sqrt() - denial of service", 0},
    {"mysql", "5.7", "CVE-2023-21977", 4.9, "medium",
     "MySQL Server optimizer vulnerability", 0},
    {"mysql", "8.0", "CVE-2023-21980", 7.1, "high",
     "MySQL Client privilege escalation", 1},
    {"redis", "6.", "CVE-2022-24735", 7.0, "high",
     "Redis Lua sandbox escape via crafted script", 1},
    {"redis", "7.", "CVE-2023-28856", 6.5, "medium",
     "Redis HINCRBYFLOAT denial of service", 0},
    {"postgresql", "13", "CVE-2023-2454", 7.2, "high",
     "PostgreSQL schema permission bypass", 1},
    {"postgresql", "14", "CVE-2023-2455", 5.4, "medium",
     "PostgreSQL row security policy bypass", 0},
    {"smb", "3.1.1", "CVE-2020-0796", 10.0, "critical",
     "SMBGhost - Remote code execution in SMBv3", 1},
    {"ftp", "vsftpd", "CVE-2021-3618", 7.4, "high",
     "ALPACA attack on FTP via TLS", 0},
    {"rdp", "10.0", "CVE-2019-0708", 9.8, "critical",
     "BlueKeep - Remote Desktop Services RCE", 1},
    {"mongodb", "4.", "CVE-2023-1409", 7.5, "high",
     "MongoDB TLS certificate validation bypass", 0},
    {NULL, NULL, NULL, 0, NULL, NULL, 0}
};

/* Analyze a service/port for known vulnerabilities */
int analyze_service(const char* service, const char* banner, int port,
                    char* result_json, int buffer_size) {
    int found = 0;
    char vulns_json[32768] = "[";
    int first = 1;

    for (int i = 0; VULN_DB[i].service != NULL; i++) {
        if (strcasecmp(service, VULN_DB[i].service) == 0) {
            /* Check if banner matches version pattern */
            int match = 0;
            if (banner != NULL && strlen(banner) > 0) {
                if (strstr(banner, VULN_DB[i].version_pattern) != NULL) {
                    match = 1;
                }
            } else {
                /* No banner — report as potential */
                match = 1;
            }

            if (match) {
                char entry[1024];
                snprintf(entry, sizeof(entry),
                    "%s{\"cve_id\":\"%s\",\"port\":%d,\"service\":\"%s\","
                    "\"cvss_score\":%.1f,\"severity\":\"%s\","
                    "\"description\":\"%s\",\"exploitable\":%s}",
                    first ? "" : ",",
                    VULN_DB[i].cve_id, port, service,
                    VULN_DB[i].cvss_score, VULN_DB[i].severity,
                    VULN_DB[i].description,
                    VULN_DB[i].exploitable ? "true" : "false");

                if (strlen(vulns_json) + strlen(entry) < sizeof(vulns_json) - 2) {
                    strncat(vulns_json, entry, sizeof(vulns_json) - strlen(vulns_json) - 1);
                    first = 0;
                    found++;
                }
            }
        }
    }
    strncat(vulns_json, "]", sizeof(vulns_json) - strlen(vulns_json) - 1);

    snprintf(result_json, buffer_size,
        "{\"service\":\"%s\",\"port\":%d,\"vulnerabilities_found\":%d,"
        "\"vulnerabilities\":%s,\"risk_level\":\"%s\"}",
        service, port, found, vulns_json,
        found > 3 ? "critical" : found > 1 ? "high" : found > 0 ? "medium" : "low");

    return found;
}

/* Correlate scan results with CVE database */
int correlate_scan_with_cves(const char* scan_json, char* result_json, int buffer_size) {
    /* Parse ports from scan JSON (simplified parser) */
    int total_vulns = 0;
    char all_vulns[65536] = "[";
    int first = 1;

    /* Iterate known services and check */
    const char* services[] = {"ssh", "http", "https", "mysql", "redis",
                              "postgresql", "smb", "ftp", "rdp", "mongodb", NULL};
    int ports[] = {22, 80, 443, 3306, 6379, 5432, 445, 21, 3389, 27017, 0};

    for (int i = 0; services[i] != NULL; i++) {
        /* Check if this port appears in scan results */
        char port_str[16];
        snprintf(port_str, sizeof(port_str), "\"port\":%d", ports[i]);
        if (strstr(scan_json, port_str) != NULL) {
            char service_vulns[8192];
            int count = analyze_service(services[i], "", ports[i],
                                       service_vulns, sizeof(service_vulns));
            if (count > 0) {
                /* Extract vulnerabilities array from service result */
                char* start = strstr(service_vulns, "\"vulnerabilities\":[");
                if (start) {
                    start += strlen("\"vulnerabilities\":");
                    char* end = strstr(start, "],");
                    if (end) {
                        /* Append individual vulns */
                        char extracted[4096];
                        int len = (int)(end - start + 1);
                        if (len < (int)sizeof(extracted)) {
                            strncpy(extracted, start + 1, len - 2);
                            extracted[len - 2] = '\0';
                            if (strlen(extracted) > 0) {
                                if (!first) {
                                    strncat(all_vulns, ",",
                                            sizeof(all_vulns) - strlen(all_vulns) - 1);
                                }
                                strncat(all_vulns, extracted,
                                        sizeof(all_vulns) - strlen(all_vulns) - 1);
                                first = 0;
                            }
                        }
                    }
                }
                total_vulns += count;
            }
        }
    }
    strncat(all_vulns, "]", sizeof(all_vulns) - strlen(all_vulns) - 1);

    snprintf(result_json, buffer_size,
        "{\"total_vulnerabilities\":%d,\"vulnerabilities\":%s,"
        "\"risk_score\":%.1f,\"recommendation\":\"%s\"}",
        total_vulns, all_vulns,
        total_vulns > 5 ? 9.5 : total_vulns > 2 ? 7.0 : total_vulns > 0 ? 4.0 : 0.0,
        total_vulns > 5 ? "Immediate remediation required" :
        total_vulns > 2 ? "High priority patching needed" :
        total_vulns > 0 ? "Monitor and plan remediation" : "No known vulnerabilities");

    return total_vulns;
}

/* Calculate overall risk score */
float calculate_risk_score(int open_ports, int critical_vulns,
                           int high_vulns, int medium_vulns) {
    float score = 0.0;
    score += open_ports * 0.1;
    score += critical_vulns * 3.0;
    score += high_vulns * 2.0;
    score += medium_vulns * 1.0;
    if (score > 10.0) score = 10.0;
    return score;
}
