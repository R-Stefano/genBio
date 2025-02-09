from absl import flags
import tensorflow as tf
import numpy as np
import obonet
import pickle
import os
import yaml
import importlib.util

import evaluate.custom_metrics as custom
import prepare.tfapiConverter as tfconv

FLAGS = flags.FLAGS

'''
This script is used to assess the quality of the model's 
predictios using the metrics defined in the CAFA challenge.

TODO:
-Threshold for predictions to 1 or 0. pred_threshold. Which value should have? 
'''

dataPath=FLAGS.dataPath
pred_threshold=0.8
model_version="version_6"
modelPath='evaluate/models/'+model_version

evaluator=custom.Evaluator()

with open("hyperparams.yaml", 'r') as f:
	hyperparams=yaml.safe_load(f)

def displayResults():
	print('\n\nRESULTS:\n')
	protein_centric_data=evaluator.resultsProteinCentricMetric()
	go_term_centric_data=evaluator.resultsGOTermCentricMetric()
	go_class_centric_data=evaluator.resultsGOClassCentricMetric()

	results={
		'model':model_version,
		'protein_centric': protein_centric_data,
		'go_term_centric': go_term_centric_data,
		'go_class_centric': go_class_centric_data
	}

	with open(modelPath+"/results", 'wb') as f:
		pickle.dump(results, f, protocol=pickle.HIGHEST_PROTOCOL)
	

def evaluate():
	#params
	batch_size=64

	#1. LOAD MODEL
	print('>Loading model')
	spec = importlib.util.spec_from_file_location("module.name", modelPath+"/model.py")
	netModule = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(netModule)
	model=netModule.Model()
	model.load_weights(modelPath+"/savedModel")

	#2. LOAD TEST EXAMPLES
	print('>Loading data')
	ex_folder=os.path.join(dataPath,'test/')
	test_files=[ex_folder+fn for fn in os.listdir(ex_folder)]
	dataset=tf.data.TFRecordDataset(test_files)

	dataset= dataset.map(tfconv.decodeTFRecord)
	dataset=dataset.batch(batch_size)

	print('>Processing data')
	for idx, batch in enumerate(dataset):
		print('>Batch', idx+1)
		#model prediction:
		model_preds,_=model.predict(batch['X'])

		#3 METRICS:
		evaluator.updateProteinCentricMetric(batch['Y'], model_preds)
		evaluator.updateGOTermCentricMetric(batch['Y'], model_preds)
		evaluator.updateGOClassCentricMetric(batch['Y'], model_preds)


	displayResults()
