#! /usr/bin/env sh

# scripts/desktop.sh

get_desktop() {
    DESKTOP='UNKNOWN'
    # bspwm
    ps -e | grep -E --quiet '^.* bspwm$'
    if [ $? -eq 0 ]; then
        DESKTOP='bspwm'
        VERSION=`bspwm -v | awk '{print "bspwm " $1}'`
        PID=`pidof bspwm`
    fi
    # Budgie
    ps -e | grep -E --quiet '^.* budgie-wm$'
    if [ $? -eq 0 ]; then
        DESKTOP='Budgie'
        VERSION=`budgie-desktop --version | grep budgie`
        PID=`pidof budgie-desktop`
    fi
    # Cinnamon
    ps -ef | grep -E --quiet '^.* cinnamon$'
    if [ $? -eq 0 ]; then
        DESKTOP='Cinnamon'
        VERSION=`cinnamon --version`
        PID=`pidof cinnamon`
    fi
    # dwm
    ps -e | grep -E --quiet '^.* dwm$'
    if [ $? -eq 0 ]; then
        DESKTOP='dwm'
        VERSION=`/usr/local/bin/dwm -v 2>&1 | tr -d '\n'`
        PID=`pidof dwm`
    fi
    # GNOME
    ps -ef | grep --quiet gnome-shell$
    if [ $? -eq 0 ]; then
        DESKTOP='Gnome'
        VERSION=`gnome-shell --version`
        PID=`pidof gnome-shell`
    fi
    # herbstluftwm
    ps -e | grep -E --quiet '^.* herbstluftwm$'
    if [ $? -eq 0 ]; then
        DESKTOP='herbstluftwm'
        VERSION=`herbstluftwm --version | grep herbstluftwm`
        PID=`pidof herbstluftwm`
    fi
    # hyprland
    ps -e | grep -E --quiet '^.* Hyprland$'
    if [ $? -eq 0 ]; then
        DESKTOP='Hyprland'
        VERSION="$DESKTOP `hyprctl -j version | jq --raw-output '. | "\(.tag) commit \(.commit) (\(.commit_date))"'`"
        PID=`pidof Hyprland`
    fi
    # i3
    ps -e | grep -E --quiet '^.* i3$'
    if [ $? -eq 0 ]; then
        DESKTOP='i3'
        VERSION=`i3 --version | sed -e 's/) .*/)/'`
        PID=`pidof i3`
    fi
    # KDE
    ps -e | grep -E --quiet '^.* plasmashell$'
    if [ $? -eq 0 ]; then
        DESKTOP='KDE'
        VK=`kded6 --version 2> /dev/null`
        VP=`plasmashell --version 2> /dev/null`
        VERSION="$VK\n$VP"
        PID=`pidof kded6`
    fi
    # MangoWC
    ps -e | grep -E --quiet '^.* mango$'
    if [ $? -eq 0 ]; then
        DESKTOP='MangoWC'
        VERSION=`mango -v 2>&1`
        PID=`pidof mango`
        export WAYLAND_DISPLAY='wayland-0'
    fi
    # MATE
    ps -e | grep -E --quiet '^.* mate-session$'
    if [ $? -eq 0 ]; then
        DESKTOP='MATE'
        VERSION=`mate-session --version`
        PID=`pidof mate-session`
    fi
    # niri
    ps -e | grep -E --quiet '^.* niri-session$'
    if [ $? -eq 0 ]; then
        DESKTOP="niri"
        VERSION=`niri --version`
        PID=`pidof -x niri-session`
    fi
    # Qtile
    ps -e | grep -E --quiet '^.* qtile$'
    if [ $? -eq 0 ]; then
        DESKTOP='Qtile'
        VERSION=`/home/zezo/.local/bin/qtile --version | awk '{print "Qtile " $1}'`
        PID=`pidof -x qtile`
    fi
    # scroll
    ps -e | grep -E --quiet '^.* scroll$'
    if [ $? -eq 0 ]; then
        DESKTOP='scroll'
        VERSION=`scroll --version`
        PID=`pidof scroll`
    fi
    # sway
    ps -e | grep -E --quiet '^.* sway$'
    if [ $? -eq 0 ]; then
        DESKTOP='sway'
        VERSION=`sway --version`
        PID=`pidof sway`
    fi
    # Xfce
    ps -e | grep -E --quiet '^.* xfce4-session$'
    if [ $? -eq 0 ]; then
        DESKTOP='Xfce'
        VERSION=`xfce4-session --version | grep xfce4-session | awk '{print "Xfce " $2}'`
        PID=`pidof xfce4-session`
    fi
}

get_desktop
