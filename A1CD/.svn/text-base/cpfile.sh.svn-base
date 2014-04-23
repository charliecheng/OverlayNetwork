#!/bin/bash

IFS=$'\r\n' hosts=($(cat 15nodes))
for i in {0..16}
do
	scp -i ~/.ssh/yucheng -P 22022 ./*  yucheng@${hosts[$i]}:/home/yucheng/overlayCD
done