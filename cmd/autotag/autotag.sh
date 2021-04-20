
# param1=$1
# echo $param1

git_branch_name=$1 
git_dir=$2

cd ${git_dir}

set_tag_time_tmp=$(date "+%Y%m%d")
set_tag_time=${set_tag_time_tmp:2}

git_cur_name=$(git rev-parse --abbrev-ref HEAD)
git checkout ${git_branch_name}
git pull
git fetch --tags
# LatestTag=$(git describe --tags `git rev-list --tags --max-count=1`)
LatestTag=$(git describe --tags --always)
arr=${LatestTag//./ }
count=0
for each in ${arr[*]}
do 
	if [ $count -eq 0 ] 
	then
		get_git_branch_name=$each
	fi
	if [ $count -eq 1 ] 
	then
		get_tag_time=$each
	fi
	if [ $count -eq 2 ] 
	then
		get_git_index=$each
	fi
	((count++))
done
new_tag=""

new_tmp=$(git tag | grep ${git_branch_name}.${set_tag_time})
array=(${new_tmp//./ })
get_git_index=${array[${#array[*]}-1]}
if [ ${git_branch_name} == $get_git_branch_name ]
then
	if [ ${set_tag_time} == $get_tag_time ] 
	then
		idx=${get_git_index: 0: 2}
		# array=${arr[2]//-/ }
		new_idx=$((10#${idx}+1))
		new_idx_str=${new_idx}
		if [ ${new_idx} -lt 10 ]
		then
			new_idx_str="0${new_idx}"
		fi
		new_tag="${git_branch_name}.${set_tag_time}.${new_idx_str}"
	else
		new_tag="${git_branch_name}.${set_tag_time}.01"
	fi
else
	new_tag="${git_branch_name}.${set_tag_time}.01"
fi
git -c diff.mnemonicprefix=false -c core.quotepath=false -c credential.helper=sourcetree tag -a -m ${new_tag} ${new_tag}
git -c diff.mnemonicprefix=false -c core.quotepath=false -c credential.helper=sourcetree push -v origin refs/tags/${new_tag}
# git tag ${new_tag}
# git push origin ${new_tag}
echo "生成新的tag:$new_tag"
git checkout ${git_cur_name}