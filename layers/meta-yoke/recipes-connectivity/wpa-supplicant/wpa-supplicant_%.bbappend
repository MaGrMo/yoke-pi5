# The WiFi network is set by build.sh via site.conf (WIFI_SSID / WIFI_PSK / WIFI_COUNTRY).
# Without WIFI_SSID poky's default config is kept.
WIFI_SSID ??= ""
WIFI_PSK ??= ""
WIFI_COUNTRY ??= "UA"

# The secrets never reach the shell code (a quote in them would break parsing):
# the SSID is written as hex and the passphrase as the derived 256-bit PSK,
# same as `wpa_passphrase` does, so the plain password is not stored in the image.
def yoke_wifi_ssid_hex(d):
    return d.getVar('WIFI_SSID').encode().hex()

def yoke_wifi_psk_hex(d):
    import hashlib
    ssid = d.getVar('WIFI_SSID').encode()
    psk = d.getVar('WIFI_PSK').encode()
    if not ssid:
        return ''
    if not 8 <= len(psk) <= 63:
        bb.fatal('WIFI_PSK must be 8..63 characters long')
    return hashlib.pbkdf2_hmac('sha1', psk, ssid, 4096, 32).hex()

# No heredoc here: bitbake ends a shell function at the first "}" in column 0,
# which would be the closing brace of the network block.
do_install:append() {
    if ${@'true' if d.getVar('WIFI_SSID') else 'false'}; then
        conf=${D}${sysconfdir}/wpa_supplicant.conf
        echo 'ctrl_interface=/var/run/wpa_supplicant' > $conf
        echo 'ctrl_interface_group=0' >> $conf
        echo 'update_config=1' >> $conf
        echo 'country=${WIFI_COUNTRY}' >> $conf
        echo '' >> $conf
        echo 'network={' >> $conf
        echo '    ssid=${@yoke_wifi_ssid_hex(d)}' >> $conf
        echo '    psk=${@yoke_wifi_psk_hex(d)}' >> $conf
        echo '    key_mgmt=WPA-PSK' >> $conf
        echo '}' >> $conf
        chmod 600 $conf
    fi
}
