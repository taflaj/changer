#! /usr/bin/env sh

# scripts/wallpaper.sh

get_env() {
    if [ -z $DBUS_SESSION_BUS_ADDRESS ]; then
        TMPEXP='/tmp/changer_exports.sh'
        EXP=`grep -z ^DBUS_SESSION_BUS_ADDRESS /proc/$PID/environ | tr -d '\0'`
        echo export $EXP > $TMPEXP
        EXP=`grep -z ^DISPLAY /proc/$PID/environ | tr -d '\0'`
        if [ ${#EXP} -gt 0 ]; then
            echo export $EXP >> $TMPEXP
        fi
        EXP=`grep -z ^XDG_RUNTIME_DIR /proc/$PID/environ | tr -d '\0'`
        echo export $EXP >> $TMPEXP
        if [ -f $TMPEXP ]; then
            source $TMPEXP
        fi
    fi
}

source scripts/desktop.sh
get_env
if [ "$DESKTOP" = "bspwm" ] || [ "$DESKTOP" = "dwm" ] || [ "$DESKTOP" = "herbstluftwm" ] || [ "$DESKTOP" = "i3" ] || [ "$DESKTOP" = "Qtile" ]; then
    # nitrogen --set-centered "$WALLPAPER"
    feh --bg-center "$1"
elif [ "$DESKTOP" = "Budgie" ] || [ "$DESKTOP" = "Gnome" ]; then
    gsettings set org.gnome.desktop.background picture-uri "file://$1"
    gsettings set org.gnome.desktop.background picture-uri-dark "file://$1"
    # If PaperWM is enabled, then it's not enough to change the file; you must also change the filename
    gnome-extensions list --enabled | grep --quiet paperwm
    if [ $? -eq 0 ]; then
        WP=/tmp/changer_wallpaper_`date +'%Y%m%d_%H%M%S'`.jpeg
        cp -p $1 $WP
        dconf write /org/gnome/shell/extensions/paperwm/default-background "'$WP'"
    fi
elif [ "$DESKTOP" == "Cinnamon" ]; then
    gsettings set org.cinnamon.desktop.background picture-uri "file://$1"
elif [ "$DESKTOP" == "Hyprland" ]; then
    # MONITOR=`hyprctl monitors | head -1 | awk '{print $2}'`
    MONITOR=`hyprctl monitors | head -1 | cut -d ' ' -f 2`
    (hyprctl hyprpaper unload $1 && hyprctl hyprpaper preload $1 && hyprctl hyprpaper wallpaper "$MONITOR, $1") > /dev/null
    # If you have the swww daemon running, you could comment out the lines above out and uncomment the one below
    # swww img "$1"
elif [ "$DESKTOP" = "KDE" ]; then
    # It's not enough to change the file; you must also change the filename
    WP=/tmp/changer_wallpaper_`date +'%Y%m%d_%H%M%S'`.jpeg
    cp -p $1 $WP
    plasma_qdbus_script="
        desktops().forEach(d => {
            d.currentConfigGroup = Array(
                \"Wallpaper\",
                \"org.kde.image\",
                \"General\");
            d.writeConfig(\"Image\", \"file://$WP\");
            d.reloadConfig();
        });"
    dbus-send --session --type=method_call --dest=org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript string:"$plasma_qdbus_script"
    dbus_exitcode="$?"
    if [[ "$dbus_exitcode" -eq 0 && "${KDE_SESSION_VERSION}" -eq '6' ]]; then
        # Update KDE lock screen background with a blurred copy
        magick $WP -channel RGBA -blur $2 $1
        kwriteconfig6 --file kscreenlockerrc --group Greeter --group Wallpaper --group org.kde.image --group General --key Image "$1"
    fi
elif [ "$DESKTOP" = "MATE" ]; then
    gsettings set org.mate.background picture-filename "$1"
elif [ "$DESKTOP" = "niri" ]; then
    swww img "$1"
elif [ "$DESKTOP" = "sway" ]; then
    export SWAYSOCK=$(ls /run/user/1000/sway-ipc.* | head -n 1)
    swaymsg "output * bg $1 center" > /dev/null
elif [ "$DESKTOP" = "Xfce" ]; then
    xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor$I/workspace0/image-style -s 5
    xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor$I/workspace0/last-image -s "$1"
fi
# a little break before removing temporary files
sleep 1
