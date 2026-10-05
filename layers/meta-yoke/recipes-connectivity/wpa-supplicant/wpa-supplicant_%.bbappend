# The WiFi network is set by build.sh via site.conf (WIFI_SSID / WIFI_PSK / WIFI_COUNTRY).
# Without WIFI_SSID poky's default config is kept.
WIFI_SSID ??= ""
WIFI_PSK ??= ""
WIFI_COUNTRY ??= "UA"

# No heredoc here: bitbake ends a shell function at the first "}" in column 0,
# which would be the closing brace of the network block.
do_install:append() {
    if [ -n "${WIFI_SSID}" ]; then
        conf=${D}${sysconfdir}/wpa_supplicant.conf
        echo 'ctrl_interface=/var/run/wpa_supplicant' > $conf
        echo 'ctrl_interface_group=0' >> $conf
        echo 'update_config=1' >> $conf
        echo 'country=${WIFI_COUNTRY}' >> $conf
        echo '' >> $conf
        echo 'network={' >> $conf
        echo '    ssid="${WIFI_SSID}"' >> $conf
        echo '    psk="${WIFI_PSK}"' >> $conf
        echo '    key_mgmt=WPA-PSK' >> $conf
        echo '}' >> $conf
        chmod 600 $conf
    fi
}
