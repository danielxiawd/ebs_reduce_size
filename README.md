# ebs_reduce_size

因为EBS卷目前只支持扩容，无法直接缩减，此脚本可以自动将EBS的容量缩小。实现的原理是先创建一个新的EBS卷挂载到EC2上，将数据同步到新的数据盘上，然后将老的EBS卷卸载。这个脚本的执行模式和结果如下：

----------------------------------------------------------------------------
$ python3 ebs_reduce_size.py --instance_id i-02896be77fc1c18ee --instance_ip 52.80.240.170 --origin_volume_id vol-0eef81a7683330018 --az cn-north-1a --newvolumesize 6 --source_data_mountpoint_path /data1

Please make sure you have backup the instance to AMI, if you have done, enter yes.(yes/no): yes
Start EBS Resizing!
vol-04ce7c93bb59764f0 is creating...
vol-04ce7c93bb59764f0 was created successfully
meta-data=/dev/sdk               isize=512    agcount=4, agsize=393216 blks
         =                       sectsz=512   attr=2, projid32bit=1
         =                       crc=1        finobt=1, sparse=0
data     =                       bsize=4096   blocks=1572864, imaxpct=25
         =                       sunit=0      swidth=0 blks
naming   =version 2              bsize=4096   ascii-ci=0 ftype=1
log      =internal log           bsize=4096   blocks=2560, version=2
         =                       sectsz=512   sunit=0 blks, lazy-count=1
realtime =none                   extsz=4096   blocks=0, rtextents=0
Sync the data from original volume to new volume.
sending incremental file list
./
file1
              0 100%    0.00kB/s    0:00:00 (xfr#1, to-chk=2/4)
file2
              0 100%    0.00kB/s    0:00:00 (xfr#2, to-chk=1/4)
lost+found/
Remount back to the source file.
Remove the tmp file.
vol-0eef81a7683330018 detached successfully
i-02896be77fc1c18ee restarted successfully


Note: 执行此脚本需要带几个参数
--instance_id：要操作的实例id
--origin_volume_id: 要被替换的volume id
--az: 新的ebs卷创建所在的可用区，需要和EC2实例所在的可用区保持一致
--newvolumesize: 新创建的EBS卷的大小（需要根据用户的判断选择合适的新卷大小）
--source_data_mountpoint_path: 原有数据盘的mount point路径，即要同步到新盘的原始数据在操作系统中的路径
-------------------------------------------------------------------------------

因为涉及到数据盘，请务必现在测试环境完成测试后再应用到其它机器上。程序开始的时候会提示先对实例做AMI备份。
 
1.  该脚本目前只适用于linux的操作系统
2.  在执行脚本期间，对应的EC2会有stop和重启的过程，所以会有down机时间
3.  该脚本目前只适用于数据盘，root盘的缩减不适用
4.  该脚本没有加载aksk或者assume role. 用的当前profile配置的aksk来执行各种命令，执行该脚本需要先配置cli profile
5.  新创建的EBS volume默认用的设备名是/dev/sdk, 如果需要更改，需要在脚本中替换/dev/sdk为其它设备名
6. 该脚本并不对卸载后的EBS卷进行删除动作，需要手动做。

