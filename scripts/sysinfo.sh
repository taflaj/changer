#! /usr/bin/env sh

# scripts/sysinfo.sh

P=`uptime --pretty | sed -e 's/u/U/'`
S=`uptime --since`
echo $P since $S > $1
python3 --version >> $1
magick -version | grep Version | sed -e 's/Version: //' -e 's/http.*$//' >> $1
source scripts/desktop.sh
echo -e $VERSION >> $1
$SHELL --version | head -1 >> $1
uname -norv >> $1
source /etc/os-release
if [ -e /etc/lsb-release ]; then
    source /etc/lsb-release
fi
if [ "$ID" = "manjaro" ]; then
    echo "$NAME $DISTRIB_RELEASE \"$DISTRIB_CODENAME\"" >> $1
elif [ "$ID" = "nixos" ]; then
    GEN=`nixos-rebuild list-generations --json | jq --raw-output '.[] | select(.current == true) | .generation, .nixosVersion, .date'`
    printf "%s %s %s #%d version %s %s\n" ${PRETTY_NAME[0]} ${PRETTY_NAME[1]} ${PRETTY_NAME[2]} $GEN >> $1
elif [ -z "$VERSION_CODENAME" ]; then
    echo $PRETTY_NAME >> $1
else
    echo $PRETTY_NAME \"$VERSION_CODENAME\" >> $1
fi
ip -br a | grep -v 127.0.0.1 | awk '{split($0, ip, " ")} {print $1 ":"} {for (i = 3; i <= length(ip); i++) print "  " ip[i]}' >> $1
# external IP address and other info
curl --silent "ipinfo.io/?token=$3" |
    jq --join-output '. | "\(.ip) \(.city)/\(.region)/\(.postal)/\(.country) (\(.org))"' \
    >> $1
