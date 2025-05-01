mkdir -p models
cd models
wget -O depth_model.pth "drive.google.com/u/3/uc?id=1R9EV9HpdWWITr6-fROibcx6C-42BETj-&export=download&confirm=yes"
wget -O panoptic_model.pth "drive.google.com/u/3/uc?id=1R8MhPBc-8wke5TMAs-tIM5h07x3fB1_d&export=download&confirm=yes"
wget -O state_estimator.pth "drive.google.com/u/3/uc?id=1pSEm3qaowRdiddEAMWohpCgwppbI6SQ_&export=download&confirm=yes"

mkdir -p subgoal_predictor
cd subgoal_predictor
wget -O tokenizer.zip "drive.google.com/u/3/uc?id=1XnMnNhC3l8gDBHVm8gAI2P1xxXKsda7F&export=download&confirm=yes"
unzip -q tokenizer.zip && rm tokenizer.zip
wget -O args.json "drive.google.com/u/3/uc?id=1k6Mfkgks-I8mYChFbYhJpRH5DMA-g0Ak&export=download&confirm=yes"
wget -O ckpt.pth "drive.google.com/u/3/uc?id=1i7mOY7NgcGVZjjBR7nwNeE_XJk0pz1Y3&export=download&confirm=yes"
