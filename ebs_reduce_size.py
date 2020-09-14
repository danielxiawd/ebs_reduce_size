"""
#Author: Xia Weidong
#Time: 2019-10-20
#Function: This script is used for helping auto shrink EBS volume.
"""
import boto3
import argparse
import time
import subprocess


def safety_check():
    answer = input('Please make sure you have backup the instance to AMI, if you have done, enter yes.(yes/no): ')
    if answer == 'yes':
        print("Start EBS Resizing!")
        return True
    else:
        print("Please backup the target instance first.")
        return False


def terminal_function(command, ip):
    key_path = '/Users/weidox/documents/lab/emrkp.pem'
    tmp_command = 'ssh -i ' + key_path + ' ec2-user@' + ip + ' \"' + command + '\"'
    print(tmp_command)
    result = subprocess.call(tmp_command, shell=True)
    return result


def stopinstance(instanceid):
    '''
    This function is used for stopping instance, adding function of checking completion status. if not complete, continue waiting
    '''
    # Stop the instance
    ec2.instances.filter(InstanceIds=[instanceid]).stop()

    # Check if stop  completes successfully or not

    while True:

        if ((ec2.Instance(instanceid).state)['Code']==80):
            break
        else:
            # Commands on all Instances were executed
            continue
    print(instanceid + ' stopped successfully')


def unattachvolume(instanceid, volumeid):

    ec2.Instance(instanceid).detach_volume(VolumeId=volumeid)

    while True:

        if (ec2.Volume(volumeid).state=='available'):
            break
        else:
            # Commands on all Instances were executed
            continue

    print(volumeid + ' detached successfully')


def createvolume(instance_id):

    response = ec2.create_volume (
        AvailabilityZone=az,
        Size=newvolumesize,
        VolumeType='gp2',
    )

    new_volume_id = response.id

    while True:
        # Attach the new created ebs volume to instance
        if (ec2.Volume(new_volume_id).state == 'available'):
            ec2.Instance(instance_id).attach_volume(VolumeId=new_volume_id, Device='/dev/sdk')
        elif(ec2.Volume(new_volume_id).state == 'in-use'):
            # Commands on all Instances were executed
            break
        else:
            continue

    # Wait for 2 minutes for disk ready after attaching
    print(new_volume_id + ' is creating...')
    time.sleep(120)
    print(new_volume_id + ' was created successfully')


def my_test():
    # result = terminal_function('sudo blkid | grep xvdk | awk \'{print $2  \\"    %s'%(
    # target_data_mountpoint_path)+'       xfs    defaults,nofail  0  2\\"}\' >>/home/ec2-user/test.txt', ec2_ip)
    result = terminal_function('sudo echo \\"/dev/sdk    %s' % source_data_mountpoint_path + 'xfs    defaults,nofail  '
                                                                                             '0  2\\" '
                                                                                             '>>/home/ec2-user/test.txt', ec2_ip)
    print(result)


def my_update_resize():
    """
    Thsi funcion won't change the file name
    """
    # Create volume
    createvolume(instance_id)

    # Mount the volume; tested multiple times, ssm didn't work consitently, therefore make the file system directly
    terminal_function('sudo mkfs -t xfs /dev/sdk', ec2_ip)

    # Create new data folder
    terminal_function('sudo mkdir /ebs_resize_data_tmp'+'', ec2_ip)

    # Mount the new volume to /data2
    terminal_function('sudo mount /dev/sdk  /ebs_resize_data_tmp'+'', ec2_ip)

    # Sync the data from original volume to new volume
    print("Sync the data from original volume to new volume.")
    result = terminal_function('sudo rsync -aHAXxSP %s' % source_data_mountpoint_path + '/  /ebs_resize_data_tmp' + '/', ec2_ip)

    # Remount to the source file
    print("Remount back to the source file.")
    terminal_function('sudo mount /dev/sdk  %s' % source_data_mountpoint_path + '', ec2_ip)

    # Delete the tmp file
    print("Remove the tmp file.")
    terminal_function('sudo rm -rf ebs_resize_data_tmp' + '', ec2_ip)

    # backup fstab before editing
    result = terminal_function('sudo chmod 777 /etc/fstab', ec2_ip)
    result = terminal_function('sudo cp /etc/fstab /etc/fstab.orig2', ec2_ip)

    # Add new volume to fstab for consistent after reboot
    result = terminal_function('sudo echo \\"/dev/sdk    %s' % (
        source_data_mountpoint_path) + '       xfs    defaults,nofail  0  2\\" >>/etc/fstab', ec2_ip)

    # Stop instance
    ec2.instances.filter(InstanceIds=[instance_id]).stop()

    time.sleep(60)

    # Unattach original data volume, need sometime to perform
    unattachvolume(instance_id, origin_volume_id)
    time.sleep(30)

    # Start instance
    instance.start_instances(InstanceIds=[instance_id])
    print(instance_id + ' restarted successfully')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument("--instance_id", type=str, default="0")
    parser.add_argument("--instance_ip", type=str, default="0")
    parser.add_argument("--origin_volume_id", type=str, default="0")
    parser.add_argument("--az", type=str, default="0")
    parser.add_argument("--newvolumesize", type=int, default=0)
    parser.add_argument("--source_data_mountpoint_path", type=str, default="0")

    args = parser.parse_args()

    instance_id =args.instance_id
    ec2_ip = args.instance_ip
    origin_volume_id = args.origin_volume_id
    az =args.az
    newvolumesize =args.newvolumesize

    source_data_mountpoint_path = args.source_data_mountpoint_path

    # Define boto3 used api
    ec2 = boto3.resource('ec2')
    instance = boto3.client('ec2')
    if safety_check():
        # my_test()
        my_update_resize()