# The WiFi network is set by build.sh via site.conf (WIFI_SSID / WIFI_PSK / WIFI_COUNTRY).
# Without WIFI_SSID poky's default config is kept.
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
