IFS=$'\r\n' hosts=($(cat 15nodes))
for i in {0..16}
do
	ssh -t -t -i ~/.ssh/yucheng -p 22022 yucheng@${hosts[$i]} "kill -9 \$(ps -A -o pid,cmd|grep 'overlay.py -m'| grep -v grep |head -n 1 | awk '{print \$1}')"
done