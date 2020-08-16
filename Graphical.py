 
#After change to a text console (pressing Ctrl+Alt+F2) and logging in as root, use the following command to disable the graphical target, which is what keeps the display manager running:
#stop x
{ '' : ['systemctl isolate multi-user.target',
    "",
    ""]
}
# set default to text
{ '' : ['sudo systemctl set-default multi-user.target',
    "",
    ""]
}
{ '' : ['sudo systemctl set-default runlevel3.target',
    "",
    ""]
}
#At this point, I'd expect you'd be able to unload the Nvidia drivers using modprobe -r (or rmmod directly):

{ '' : ['modprobe -r nvidia-drm',
    "",
    ""]
}

#Once you've managed to replace/upgrade it and you're ready to start the graphical environment again, you can use this command:
# start x
{ '' : ['systemctl start graphical.target',
    "",
    ""]
}

#set default to x
{ '' : ['sudo systemctl set-default graphical.target',
    "",
    ""]
}
{ '' : ['sudo systemctl set-default runlevel5.target',
    "",
    ""]
}
# As the error message said, if you are running 
# nvidia-persistenced, you'll need to stop that too before you can unload the nvidia_drm module.