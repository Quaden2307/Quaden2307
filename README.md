<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Quaden2307/Quaden2307/main/assets/name-dark.svg">
  <img alt="Caden Sun" src="https://raw.githubusercontent.com/Quaden2307/Quaden2307/main/assets/name-light.svg" width="464">
</picture>
<br>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Quaden2307/Quaden2307/main/assets/contributions-dark.svg">
  <img alt="Contribution graph for the last year" src="https://raw.githubusercontent.com/Quaden2307/Quaden2307/main/assets/contributions-light.svg" width="100%">
</picture>

Hi! I'm a Mathematics student at the University of Waterloo, class of 2029. I'm into Software Engineering, Machine Learning, and AI, and always looking for opportunities to build something great. My past experience includes interning as an AI Engineer at **[ProCogia](https://procogia.com)**, and in Winter 2027 I'm joining **[Bits in Glass](https://bitsinglass.ai)** as a Machine Learning Engineer Intern. In my free time I like to play the piano, hoops + eats, and going on walks. 

### Contact

Email is the best way to reach me: [c262sun@uwaterloo.ca](mailto:c262sun@uwaterloo.ca). I'm also on [LinkedIn](https://www.linkedin.com/in/cadensun), and there's more on [my website](https://personal-website-rose-delta-47.vercel.app).

### Projects

**[Flight Price Predictor](https://github.com/Quaden2307/flight-price-predictor)** estimates what a flight should cost. A daily pipeline has collected over 400,000 fares since&nbsp;May&nbsp;2026, now across the 300 routes below, and the XGBoost model averages 14.6% error on flights held out from training, against 17.1% for a linear baseline.<br>
<picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Quaden2307/Quaden2307/main/assets/routes-dark.svg"><img alt="Map of the 300 routes between 81 airports that the flight price pipeline collects fares on every day" src="https://raw.githubusercontent.com/Quaden2307/Quaden2307/main/assets/routes-light.svg" width="100%"></picture>

**[Cat Classifier](https://github.com/Quaden2307/cat-classifier)** decides whether your cat is a ragdoll. It's a ResNet-18 convolutional network fine-tuned on a 1,722-photo dataset and run in your browser through ONNX, so the photo never leaves your device. Answering "not ragdoll" every time would already be 77% accurate, so it trains with a class-weighted loss and is judged on F1, where it scores 0.83 and catches 52 of the 60 ragdolls in the test set. [Try it](https://cat-classifier-five.vercel.app).<br>
<picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Quaden2307/Quaden2307/main/assets/cat-conv-dark.svg"><img alt="A pixel cat with a 3 by 3 window over the edge of its ear, that window enlarged, and the edge map a convolution produces" src="https://raw.githubusercontent.com/Quaden2307/Quaden2307/main/assets/cat-conv-light.svg" width="100%"></picture>

**[Chess Engine](https://github.com/Quaden2307/chess-engine)** searches with negamax, alpha-beta pruning and iterative deepening, plus quiescence search, a Zobrist-keyed transposition table, killer and history move ordering, and a tapered evaluation. It plays through a Flask API on Vercel and a React board with a live evaluation bar and candidate-move arrows. In the position below White is a queen down, and the engine finds Légal's Mate: 6.Bxf7+ Ke7 7.Nd5#. [Play against it](https://chess-bot-deployment.vercel.app).<br>
<picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Quaden2307/Quaden2307/main/assets/chess-legal-dark.svg"><img alt="Chess position with White a queen down; an arrow shows the engine's move Bxf7+, which mates in two" src="https://raw.githubusercontent.com/Quaden2307/Quaden2307/main/assets/chess-legal-light.svg" width="320"></picture>

**[Scout](https://github.com/aikhanjum/scout)** is a lidar rover my team built in 32 hours at Hack the North 2026. It checks the gaps along its path against the 860&nbsp;mm a wheelchair needs, and its lidar read one doorway at 878&nbsp;mm against an 880&nbsp;mm reference. I built the operator console's map view, made the simulator drivable, and added run controls, downloads and reports.

### Tools

**Languages:** Python, C++, C, TypeScript, JavaScript, SQL, Java\
**Machine learning:** PyTorch, scikit-learn, XGBoost, pandas, NumPy, LangGraph, ONNX\
**Web and cloud:** Flask, React, Node.js, AWS, PostgreSQL with pgvector, SQLite, Docker, Linux, Vercel
