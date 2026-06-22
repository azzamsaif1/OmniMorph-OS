#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <errno.h>
#include <fcntl.h>
#include <sys/select.h>

#define MAX_PORTS 65535
#define SCAN_TIMEOUT_MS 200
#define RESULT_BUFFER_SIZE 65536

typedef struct {
    int port;
    int is_open;
    char service[64];
} PortResult;

typedef struct {
    char target_ip[64];
    int total_ports_scanned;
    int open_ports_count;
    PortResult open_ports[1024];
    char error[256];
    int success;
} ScanResult;

static const char* get_service_name(int port) {
    switch (port) {
        case 21: return "ftp";
        case 22: return "ssh";
        case 23: return "telnet";
        case 25: return "smtp";
        case 53: return "dns";
        case 80: return "http";
        case 110: return "pop3";
        case 143: return "imap";
        case 443: return "https";
        case 445: return "smb";
        case 993: return "imaps";
        case 995: return "pop3s";
        case 3306: return "mysql";
        case 3389: return "rdp";
        case 5432: return "postgresql";
        case 5900: return "vnc";
        case 6379: return "redis";
        case 8080: return "http-proxy";
        case 8443: return "https-alt";
        case 27017: return "mongodb";
        default: return "unknown";
    }
}

static int check_port(const char* ip, int port, int timeout_ms) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) return 0;

    /* Set non-blocking */
    int flags = fcntl(sock, F_GETFL, 0);
    fcntl(sock, F_SETFL, flags | O_NONBLOCK);

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, ip, &addr.sin_addr);

    int result = connect(sock, (struct sockaddr*)&addr, sizeof(addr));
    if (result == 0) {
        close(sock);
        return 1;
    }

    if (errno != EINPROGRESS) {
        close(sock);
        return 0;
    }

    fd_set writefds;
    FD_ZERO(&writefds);
    FD_SET(sock, &writefds);

    struct timeval tv;
    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;

    result = select(sock + 1, NULL, &writefds, NULL, &tv);
    if (result > 0) {
        int so_error;
        socklen_t len = sizeof(so_error);
        getsockopt(sock, SOL_SOCKET, SO_ERROR, &so_error, &len);
        close(sock);
        return (so_error == 0) ? 1 : 0;
    }

    close(sock);
    return 0;
}

/* Scan common ports on target IP */
int scan_common_ports(const char* target_ip, char* result_json, int buffer_size) {
    int common_ports[] = {
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445,
        993, 995, 1433, 1521, 2049, 3306, 3389, 5432, 5900, 6379,
        8080, 8443, 9090, 27017, 0
    };

    int open_count = 0;
    char ports_json[32768] = "[";
    int first = 1;

    for (int i = 0; common_ports[i] != 0; i++) {
        if (check_port(target_ip, common_ports[i], SCAN_TIMEOUT_MS)) {
            char entry[128];
            snprintf(entry, sizeof(entry),
                "%s{\"port\":%d,\"service\":\"%s\",\"state\":\"open\"}",
                first ? "" : ",",
                common_ports[i],
                get_service_name(common_ports[i]));
            strncat(ports_json, entry, sizeof(ports_json) - strlen(ports_json) - 1);
            first = 0;
            open_count++;
        }
    }
    strncat(ports_json, "]", sizeof(ports_json) - strlen(ports_json) - 1);

    snprintf(result_json, buffer_size,
        "{\"target\":\"%s\",\"open_ports_count\":%d,\"ports\":%s,\"scan_type\":\"tcp_connect\",\"status\":\"complete\"}",
        target_ip, open_count, ports_json);

    return open_count;
}

/* Scan a specific port range */
int scan_port_range(const char* target_ip, int start_port, int end_port,
                    char* result_json, int buffer_size) {
    if (start_port < 1) start_port = 1;
    if (end_port > MAX_PORTS) end_port = MAX_PORTS;

    int open_count = 0;
    char ports_json[65536] = "[";
    int first = 1;

    for (int port = start_port; port <= end_port; port++) {
        if (check_port(target_ip, port, SCAN_TIMEOUT_MS)) {
            char entry[128];
            snprintf(entry, sizeof(entry),
                "%s{\"port\":%d,\"service\":\"%s\",\"state\":\"open\"}",
                first ? "" : ",",
                port,
                get_service_name(port));

            if (strlen(ports_json) + strlen(entry) < sizeof(ports_json) - 2) {
                strncat(ports_json, entry, sizeof(ports_json) - strlen(ports_json) - 1);
                first = 0;
            }
            open_count++;
        }
    }
    strncat(ports_json, "]", sizeof(ports_json) - strlen(ports_json) - 1);

    snprintf(result_json, buffer_size,
        "{\"target\":\"%s\",\"range\":\"%d-%d\",\"open_ports_count\":%d,\"ports\":%s,\"status\":\"complete\"}",
        target_ip, start_port, end_port, open_count, ports_json);

    return open_count;
}

/* Service banner grabbing */
int grab_banner(const char* target_ip, int port, char* banner, int banner_size) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) return -1;

    struct timeval tv;
    tv.tv_sec = 2;
    tv.tv_usec = 0;
    setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof(tv));
    setsockopt(sock, SOL_SOCKET, SO_SNDTIMEO, &tv, sizeof(tv));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons(port);
    inet_pton(AF_INET, target_ip, &addr.sin_addr);

    if (connect(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close(sock);
        return -1;
    }

    /* Try to read banner */
    int bytes = recv(sock, banner, banner_size - 1, 0);
    if (bytes > 0) {
        banner[bytes] = '\0';
        /* Remove non-printable chars */
        for (int i = 0; i < bytes; i++) {
            if (banner[i] < 32 && banner[i] != '\n' && banner[i] != '\r') {
                banner[i] = '.';
            }
        }
    } else {
        /* Send probe for HTTP */
        const char* probe = "HEAD / HTTP/1.0\r\n\r\n";
        send(sock, probe, strlen(probe), 0);
        bytes = recv(sock, banner, banner_size - 1, 0);
        if (bytes > 0) {
            banner[bytes] = '\0';
        } else {
            strncpy(banner, "", banner_size);
            close(sock);
            return -1;
        }
    }

    close(sock);
    return 0;
}
