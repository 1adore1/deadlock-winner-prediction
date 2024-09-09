# **Deadlock Team Win Prediction**

### Overview

The goal of this project is to predict the winning team in the new MOBA game Deadlock by Valve, based solely on the teams picks.

### Installation

1. Clone the repository:
```
git clone https://github.com/1adore1/deadlock-prediction.git
cd deadlock-prediction
```
2. Install required libraries:
```
pip install -r requirements.txt
```

### Usage

1. Preprocess the dataset by running:
```
python preprocess.py
```
2. Train the model with:
```
python train_model.py
```
3. Make predictions on your input picks:
```
python predict.py
```

### Models Used

* **Random Forest**
* **Gradient Boosting**
* **Logistic Regression**

### Data

The dataset includes match history from Deadlock, that was parsed from [tracklock.gg](https://tracklock.gg).

Dataset focused on:

* **Team picks**: Heroes chosen by each team.
* **Game results**: Outcome of the match (win/loss).
---
