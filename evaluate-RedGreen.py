import tensorflow as tf
import scripts.label_image2 as ai

greens = [
    "green.mp4_001.02.jpg",
    "green.mp4_001.48.jpg",
    "green.mp4_003.25.jpg",
    "green.mp4_006.41.jpg",
    "green.mp4_012.64.jpg",
    "green.mp4_018.87.jpg",
    "green.mp4_023.56.jpg",
    "green.mp4_025.41.jpg",
    "green.mp4_028.25.jpg",
    "green.mp4_029.18.jpg",
    ]
reds = [
    "red.mp4___000.33.jpg",
    "red.mp4___001.95.jpg",
    "red.mp4___003.56.jpg",
    "red.mp4___006.72.jpg",
    "red.mp4___009.87.jpg",
    "red.mp4___014.56.jpg",
    "red.mp4___017.72.jpg",
    "red.mp4___020.87.jpg",
    "red.mp4___024.02.jpg",
    "red.mp4___028.72.jpg",
    ]

print("\n---- greens ----")
for i in greens:
    path = "tf_files/RedGreen/Evaluation/Green-evaluation/"
    eval = ai.predict(path + i)
    print(eval)
print("\n---- reds ----")
for i in reds:
    path = r"tf_files/RedGreen/Evaluation/Red-evaluation/"
    eval = ai.predict(path + i)
    print(eval)
    
'''
    Command line for retraining:
    python -m scripts.retrain --bottleneck_dir=tf_files/bottlenecks --how_many_training_steps=1000 --model_dir=tf_files/models/ --summaries_dir=tf_files/training_summaries/"mobilenet_1.0_224" --output_graph=tf_files/retrained_graph.pb --output_labels=tf_files/retrained_labels.txt --architecture="mobilenet_1.0_224" --image_dir=tf_files/RedGreen/Training 
    
    This is my test result. It works for my training photos so the model I use 
    （mobilenet_1.0_224）can distinguish colours. This is just the starting.
    
    Next step is to mimic the same process but replace my pictures to 
    your sample and draw the traffic light to red and green. Almost the same
    experiment but will it work? To try to know about that.
    
    
    P:\>python -m evaluate-RedGreen.py

    ---- greens ----
    2018-01-26 12:46:54.932924: I C:\tf_jenkins\home\workspace\rel-win\M\windows\PY\36\tensorflow\core\platform\cpu_feature_guard.cc:137] Your CPU supports instructions that this TensorFlow binary was not compiled to use: AVX AVX2
    Evaluation time (1-image): 0.601s
    98.13% : green
     1.87% : red

    Evaluation time (1-image): 0.654s
    98.76% : green
     1.24% : red

    Evaluation time (1-image): 0.590s
    98.15% : green
     1.85% : red

    Evaluation time (1-image): 0.569s
    100.00% : green
     0.00% : red

    Evaluation time (1-image): 0.618s
    98.83% : green
     1.17% : red

    Evaluation time (1-image): 0.570s
    99.35% : green
     0.65% : red

    Evaluation time (1-image): 0.578s
    99.26% : green
     0.74% : red

    Evaluation time (1-image): 0.568s
    100.00% : green
     0.00% : red

    Evaluation time (1-image): 0.564s
    99.99% : green
     0.01% : red

    Evaluation time (1-image): 0.617s
    98.77% : green
     1.23% : red


    ---- reds ----
    Evaluation time (1-image): 0.570s
    100.00% : red
     0.00% : green

    Evaluation time (1-image): 0.563s
    99.95% : red
     0.05% : green

    Evaluation time (1-image): 0.570s
    98.29% : red
     1.71% : green

    Evaluation time (1-image): 0.548s
    75.56% : red
    24.44% : green

    Evaluation time (1-image): 0.632s
    99.93% : red
     0.07% : green

    Evaluation time (1-image): 0.586s
    99.13% : red
     0.87% : green

    Evaluation time (1-image): 0.587s
    94.89% : red
     5.11% : green

    Evaluation time (1-image): 0.570s
    81.26% : red
    18.74% : green

    Evaluation time (1-image): 0.596s
    100.00% : red
     0.00% : green

    Evaluation time (1-image): 0.587s
    100.00% : red
     0.00% : green


'''