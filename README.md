# neopets_battleground_wins
For tracking battleground of the obelisk wins


## Installation

Assuming you already have python installed, run

`pip install -r requirements.txt`


## Using the script


the script can be run as below:

`python main.py <usernames_csv_path> [<input_csv_path>] [<output_csv_path>]"`

There is an example username file, `username_example.csv`. The input and output csv paths are
not required. They will default to `default.csv` for both the input and output if nothing is
provided. It is recommended to specify the csv path though to not accidentally cause overwrites.