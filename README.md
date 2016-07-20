# blender_mdtraj_importer
Blender add-on that imports MD trajectories supported by the mdtraj project

## Installation
- Download the latest source code as ZIP archive
[blender_mdtraj_importer.zip](https://github.com/breuerss/blender_mdtraj_importer/archive/master.zip)
- Navigate to 'File' --> 'User Preferences' --> 'Add-ons' --> 'Install from File...'
- Select the downloaded archive
- Find the imported add-on in the category 'Mesh'
- Enable it by ticking the checkbox

## Prerequisites
For the add-on to work the installation of

- [mdtraj](https://github.com/mdtraj/mdtraj)
- [scipy](https://github.com/scipy/scipy)

for Python 3 is necessary.

On a Ubuntu system this can be done with
```shell
sudo apt-get install python3-pip
sudo pip3 install scipy cython numpy mdtraj
```

## Usage Quickstart
- Open Blender `blender`
- Navigate to '3D View'
- Open the left menu area
- Open the the 'MD Trajectory' tab
- Select a trajectory
- Select a topology
- Change the subset selection string to something reasonable
([Selection reference](http://mdtraj.org/1.7.2/atom_selection.html))
- Click on the 'Import' button
