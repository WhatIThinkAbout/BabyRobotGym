# BabyRobotGym
An OpenAI Gym Environment for Baby Robot


To get up and running with this simple custom Gym Environment, do the following:


## Cloning the Github repository


## 1\.&nbsp; <b><i>Get the code and move to the newly created directory</b></i>:

`git clone https://github.com/WhatIThinkAbout/BabyRobotGym.git` <br>
`cd BabyRobotGym`

* this directory contains the files and folder structure that we've defined above (plus a few extra ones that we'll look at in part 2).

<br><br>
## 2\.&nbsp; <b><i>Create a Conda environment and install the required packages</b></i>:<br>

To be able to run our environment we need to have a few other packages installed, most notably 'Gym' itself. To make it easy to setup the environment the Github repo contains a couple of '.yml' files that list the required packages. 
To use these to create a Conda environment and install the packages, do the following (choose the one appropriate for your operating system):

On Unix:

`conda env create -f environment_unix.yml`<br>


On Windows: 

`conda env create -f environment_windows.yml`<br>


<br><br>
## 3\.&nbsp; <b><i>Activate the environment</b></i>:

We've created the environment with all our required packages, so now it's just a case of activating it, as follows:

`conda activate BabyRobotGym`<br>

(when you're finished playing with this environment run "conda deactivate" to get back out)


<br><br>
## 4\.&nbsp; <b><i>Run the notebook</b></i>

Everything should now be in place to run our custom Gym environment. To test this we can run the sample Jupyter Notebook <i>'baby_robot_gym_test.ipynb'</i> that's included in the repository. This will load the _'BabyRobotEnv-v1'_ environment and test it using the Stable Baseline's environment checker. 

To start this in a browser, just type:

`jupyter notebook baby_robot_gym_test.ipynb`<br>

(When running in jupyter notebook the current Conda environment will automatically be used and the required packages should all be available. It's also possible to run "<i>python -m ipykernel install --user --name=BabyRobotGym</i>" which will create a Jupyter Notebook kernel, that can then be selected from the notebook's menu.)

Or else just open this file in VS Code and make sure _'BabyRobotGym'_ is selected as the kernel. This should make the _'BabyRobotEnv-v1'_ environment, test it in Stable Baselines and then run the environment until it completes, which happens to occur in a single step, since we haven't yet written the 'step' function!
