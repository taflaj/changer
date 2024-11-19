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

source scripts/desktop.sh ''
get_env
if [ "$DESKTOP" = "Budgie" ] || [ "$DESKTOP" = "Gnome" ]; then
    gsettings set org.gnome.desktop.background picture-uri "file://$1"
    gsettings set org.gnome.desktop.background picture-uri-dark "file://$1"
elif [ "$DESKTOP" = "bspwm" ] || [ "$DESKTOP" = "dwm" ] || [ "$DESKTOP" = "herbstluftwm" ] || [ "$DESKTOP" = "i3" ] || [ "$DESKTOP" = "Qtile" ]; then
    # nitrogen --set-centered "$WALLPAPER"
    feh --bg-center "$1"
elif [ "$DESKTOP" == "Hyprland" ]; then
    # MONITOR=`hyprctl monitors | head -1 | awk '{print $2}'`
    MONITOR=`hyprctl monitors | head -1 | cut -d ' ' -f 2`
    (hyprctl hyprpaper unload $1 && hyprctl hyprpaper preload $1 && hyprctl hyprpaper wallpaper "$MONITOR, $1") > /dev/null
elif [ "$DESKTOP" = "KDE" ]; then
    qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript "
        var allDesktops = desktops();
        print (allDesktops);
        for (i = 0; i < allDesktops.length; i++) {
            d = allDesktops[i];
            d.wallpaperPlugin = \"org.kde.image\";
            d.currentConfigGroup = Array(\"Wallpaper\", \"org.kde.image\", \"General\");
            d.writeConfig(\"Image\", \"file://$1\")
        }"
elif [ "$DESKTOP" = "MATE" ]; then
    gsettings set org.mate.background picture-filename "$1"
elif [ "$DESKTOP" = "sway" ]; then
    export SWAYSOCK=$(ls /run/user/1000/sway-ipc.* | head -n 1)
    swaymsg "output * bg $1 center" > /dev/null
elif [ "$DESKTOP" = "Xfce" ]; then
    xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor$I/workspace0/image-style -s 5
    xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor$I/workspace0/last-image -s "$1"
fi
# a little break before removing temporary files
sleep 1
