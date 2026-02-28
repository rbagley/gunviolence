#!/bin/bash
#SBATCH --account=p31502 ## Required: your allocation/account name, i.e. eXXXX, pXXXX or bXXXX
#SBATCH --partition=gengpu ## Required: (buyin, short, normal, long, gengpu, genhimem, etc)
#SBATCH --time=12:00:00 ## Required: How long will the job need to run (remember different partitions have restrictions on this parameter) 
#SBATCH --gres=gpu:a100:1
#SBATCH --constraint=sxm
#SBATCH --nodes=1 ## how many computers/nodes do you need (no default)
#SBATCH --ntasks-per-node=1 ## how many cpus or processors do you need on per computer/node (default value 1)
#SBATCH --mem=3G ## how much RAM do you need per computer/node (this affects your FairShare score so be careful to not ask for more than you need))
#SBATCH --job-name=bert_predictions ## When you run squeue -u  this is how you can identify the job
#SBATCH --output=/projects/p31502/projects/gun_violence/community_justice/bert/output/predictions_%A.txt ## standard out and standard error goes to this file
#SBATCH --export=ALL
 
# A regular comment in Bash
#module purge all 
#module load python-anaconda3
source /projects/p31502/projects/gun_violence/community_justice/bert/bert_env/bin/activate

echo "hello there $USER"
date
which python

#python framing_predictions.py
#python framing_predictions.py --group police
#python framing_predictions.py --group shooter
#python framing_predictions.py --group victim
#python contextual_embedding.py
python svm.py

#python bayes.py --filtered mentions --category speakers --division super
#python bayes.py --filtered mentions --category masked_speakers --division super
#python bayes.py --filtered mentions --category death --division super

#python bayes.py -f location -c milwaukee
#python bayes.py -f location -c detroit
#python bayes.py -f location -c midwest