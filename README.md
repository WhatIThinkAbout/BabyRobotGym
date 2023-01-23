# BabyRobotGym
### A Reinforcement Learning Gym Environment for Baby Robot


![](https://github.com/WhatIThinkAbout/BabyRobotGym/blob/main/notebooks/images/black_maze_run_opt.gif)


The code in this repository accompanies the Towards Data Science article _[<b>Creating a Custom Gym Environment for Jupyter Notebooks</b> - <i>Part 1: Creating the framework</i>](https://towardsdatascience.com/creating-a-custom-gym-environment-for-jupyter-notebooks-e17024474617)_ and shows the steps required to create a custom gym environment with graphical output in a Jupyter notebook.


![](https://github.com/WhatIThinkAbout/BabyRobotGym/blob/main/notebooks/images/green_babyrobot_small.gif)


## To install:

```
pip install babyrobot
```

# Animation Example

An example notebook showing how animation and movie creation can be done in the Baby Robot Gym environment:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/WhatIThinkAbout/BabyRobotGym/HEAD?labpath=notebooks%2FBabyRobot_Animation.ipynb)


# API Example

The example notebook, showing all of the API calls used to create a Baby Robot Gym environment can be opened here:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/WhatIThinkAbout/BabyRobotGym/HEAD?labpath=notebooks%2FBabyRobot_API.ipynb)

# Reinforcement Learning

## Part 1: [State Values and Policy Evaluation](https://towardsdatascience.com/state-values-and-policy-evaluation-ceefdd8c2369)

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/WhatIThinkAbout/BabyRobotGym/HEAD?labpath=notebooks%2FReinforcement%20Learning%2FPart%201%20-%20State%20Values%20and%20Policy%20Evaluation.ipynb)


### Training Example

An example of using the PPO Reinforcement Learning algorithm to train Baby Robot how to escape from a maze:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/WhatIThinkAbout/BabyRobotGym/blob/main/notebooks/PPO_Training.ipynb)

## Getting the Github Code:

### Testing

The test notebook, showing how to run a simple RL environment can be opened here:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/WhatIThinkAbout/BabyRobotGym/blob/main/baby_robot_gym_test.ipynb)


## Cloning the Github repository

To get up and running with this simple custom Gym Environment, do the following:


## 1\.&nbsp; <b><i>Get the code and move to the newly created directory</b></i>:

`git clone https://github.com/WhatIThinkAbout/BabyRobotGym.git` <br>
`cd BabyRobotGym`

* this directory contains the files and folder structure.

<br><br>
## 2\.&nbsp; <b><i>Create a Conda environment and install the required packages</b></i>:<br>

To be able to run our environment we need to have a few other packages installed, most notably '_Gym_' itself. To make it easy to setup the environment the Github repo contains a couple of '_.yml_' files that list the required packages. 

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


<br><br>
# Notes:

If, while running in a terminal (as opposed to a Jupyter Notebook) you get the warning "DeprecationWarning: Jupyter is migrating its paths to use standard platformdirs", in a terminal run:

`export JUPYTER_PLATFORM_DIRS=1`

followed by:

`jupyter --paths`

