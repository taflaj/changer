#! /usr/bin/env sh

# scripts/desktop.sh

get_desktop() {
    DESKTOP='UNKNOWN'
    # bspwm
    ps -e | grep -E '^.* bspwm$' > /dev/null
    if [ $? -eq 0 ]; then
        DESKTOP='bspwm'
        VERSION=`bspwm -v | awk '{print "bspwm " $1}'`
        PID=`pidof bspwm`
    fi
    # Budgie
    ps -e | grep -E '^.* budgie-wm$' > /dev/null
    if [ $? -eq 0 ]; then
        DESKTOP='Budgie'
        VERSION=`budgie-desktop --version | grep budgie`
        PID=`pidof budgie-desktop`
    fi
    # Cinnamon
    ps -e | grep -E '^.* cinnamon$' > /dev/null
    if [ $? -eq 0 ]; then
        DESKTOP='Cinnamon'
        VERSION=`cinnamon --version`
        PID=`pidof cinnamon`
    fi
    # dwm
    ps -e | grep -E '^.* dwm$' > /dev/null
    if [ $? -eq 0 ]; then
        DESKTOP='dwm'
        VERSION=`/usr/local/bin/dwm -v 2>&1 | tr -d '\n'`
        PID=`pidof dwm`
    fi
    # Gnome
    ps -e | grep -E '^.* gnome-shell$' > /dev/null
    if [ $? -eq 0 ]; then
        DESKTOP='Gnome'
        VERSION=`gnome-shell --version`
        PID=`pidof gnome-shell`
    fi
    # herbstluftwm
    ps -e | grep -E '^.* herbstluftwm$' > /dev/null
    if [ $? -eq 0 ]; then
        DESKTOP='herbstluftwm'
        VERSION=`herbstluftwm --version | grep herbstluftwm`
        PID=`pidof herbstluftwm`
    fi
    # hyprland
    ps -e | grep -E '^.* Hyprland$' > /dev/null
    if [ $? -eq 0 ]; then
        DESKTOP='Hyprland'
        VERSION="$DESKTOP `hyprctl -j version | jq -r '. | "\(.tag) commit \(.commit) (\(.commit_date))"'`"
        PID=`pidof Hyprland`
    fi
    # i3
    ps -e | grep -E '^.* i3$' > /dev/null
    if [ $? -eq 0 ]; then
        DESKTOP='i3'
        VERSION=`i3 --version | sed -e 's/) .*/)/'`
        PID=`pidof i3`
    fi
    # KDE
    ps -e | grep -E '^.* plasmashell$' > /dev/null
    if [ $? -eq 0 ]; then
        DESKTOP='KDE'
        VERSION=`kded5 --version`
        PID=`pidof kded5`
    fi
    # MATE
    ps -e | grep -E '^.* mate-session$' > /dev/null
    if [ $? -eq 0 ]; then
        DESKTOP='MATE'
        VERSION=`mate-session --version`
        PID=`pidof mate-session`
    fi
    # Qtile
    ps -e | grep -E '^.* qtile$' > /dev/null
    if [ $? -eq 0 ]; then
        DESKTOP='Qtile'
        VERSION=`/home/zezo/.local/bin/qtile --version | awk '{print "Qtile " $1}'`
        PID=`pidof -x qtile`
    fi
    # sway
    ps -e | grep -E '^.* sway$' > /dev/null
    if [ $? -eq 0 ]; then
        DESKTOP='sway'
        VERSION=`sway --version`
        PID=`pidof sway`
    fi
    # Xfce
    ps -e | grep -E '^.* xfce4-session$' > /dev/null
    if [ $? -eq 0 ]; then
        DESKTOP='Xfce'
        VERSION=`xfce4-session --version | grep xfce4-session | awk '{print "Xfce " $2}'`
        PID=`pidof xfce4-session`
    fi
}

get_desktop