# AWS_EBS_auto_shrink_update

This script is for resize the EC2 instance's EBS size.

- Without using AWS System Manager

- 

## How to use:

```shell script
python3 ebs_auto_shrink_update.py --instance_id i-001e5479fc80f545f --instance_ip 52.81.61.64 --origin_volume_id vol-0dfae56b4902770fb --az cn-north-1a --newvolumesize 6 --source_data_mountpoint_path /data1 --target_data_mountpoint_path /data9
```
