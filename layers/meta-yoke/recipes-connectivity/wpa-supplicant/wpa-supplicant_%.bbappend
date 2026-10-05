# Мережа WiFi задається з build.sh через site.conf (WIFI_SSID / WIFI_PSK / WIFI_COUNTRY).
# Без WIFI_SSID лишається стандартний конфіг poky.
WIFI_SSID ??= ""
WIFI_PSK ??= ""
WIFI_COUNTRY ??= "UA"

do_install:append() {
    if [ -n "${WIFI_SSID}" ]; then
        cat > ${D}${sysconfdir}/wpa_supplicant.conf <<'WPAEOF'
ctrl_interface=/var/run/wpa_supplicant
ctrl_interface_group=0
update_config=1
country=${WIFI_COUNTRY}

network={
    ssid="${WIFI_SSID}"
    psk="${WIFI_PSK}"
    key_mgmt=WPA-PSK
}
WPAEOF
        chmod 600 ${D}${sysconfdir}/wpa_supplicant.conf
    fi
}
