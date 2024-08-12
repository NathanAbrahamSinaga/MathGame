<script>
  import { onMount, onDestroy } from 'svelte';
  import { fade, fly } from 'svelte/transition';

  let playerName = '';
  let gameStarted = false;
  let gameEnded = false;
  let currentQuestion = '';
  let answer = '';
  let score = 0;
  let timeLeft = 60;
  let timer;
  let highScores = [];
  let showNameInput = false;

  let introAudio, gameAudio, endAudio;

  onMount(() => {
    fetchHighScores();
    initAudio();
  });

  onDestroy(() => {
    stopAllAudio();
    clearInterval(timer);
  });

  function initAudio() {
    introAudio = new Audio('/audio/intro-music.mp3');
    gameAudio = new Audio('/audio/game-music.mp3');
    endAudio = new Audio('/audio/end-music.mp3');
    introAudio.loop = true;
    gameAudio.loop = true;
  }

  function playIntroAudio() {
    introAudio.play().catch(error => console.error('Audio playback failed:', error));
  }

  function stopAllAudio() {
    [introAudio, gameAudio, endAudio].forEach(audio => {
      if (audio && typeof audio.pause === 'function') {
        audio.pause();
        audio.currentTime = 0;
      }
    });
  }

  function handleStart() {
    playIntroAudio();
    showNameInput = true;
  }

  function startGame() {
    if (playerName.trim() === '') return;
    stopAllAudio();
    gameAudio.play().catch(error => console.error('Audio playback failed:', error));
    gameStarted = true;
    gameEnded = false;
    score = 0;
    timeLeft = 90;
    nextQuestion();
    timer = setInterval(() => {
      timeLeft--;
      if (timeLeft <= 0) endGame();
    }, 1000);
  }

  function nextQuestion() {
    const num1 = Math.floor(Math.random() * 10) + 1;
    const num2 = Math.floor(Math.random() * 10) + 1;
    const operation = ['*', '+', '-'][Math.floor(Math.random() * 3)];
    currentQuestion = `${num1} ${operation} ${num2}`;
  }

  function checkAnswer() {
    const correctAnswer = eval(currentQuestion);
    if (parseInt(answer) === correctAnswer) {
      score++;
    }
    answer = '';
    nextQuestion();
  }

  async function endGame() {
    clearInterval(timer);
    gameStarted = false;
    gameEnded = true;
    stopAllAudio();
    endAudio.play().catch(error => console.error('Audio playback failed:', error));
    
    try {
      const response = await fetch('http://localhost:8000/api/players/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: playerName, score, time: 60 - timeLeft })
      });

      if (response.ok) {
        fetchHighScores();
      } else {
        console.error('Failed to save score');
      }
    } catch (error) {
      console.error('Error saving score:', error);
    }
  }

  async function fetchHighScores() {
      try {
          const response = await fetch('http://localhost:8000/api/players/');
          if (response.ok) {
          highScores = await response.json();
          console.log('High scores:', highScores);
          } else {
          console.error('Failed to fetch high scores');
          }
      } catch (error) {
          console.error('Error fetching high scores:', error);
      }
  }

  function resetGame() {
    gameEnded = false;
    playerName = '';
    score = 0;
    showNameInput = false;
    stopAllAudio();
  }
</script>

<main class="min-h-screen bg-gradient-to-br from-purple-400 to-indigo-600 flex items-center justify-center">
<div class="bg-white p-8 rounded-lg shadow-2xl w-full max-w-md">
  {#if !gameStarted && !gameEnded}
    <div in:fade="{{ duration: 500 }}">
      <h1 class="text-4xl font-bold mb-6 text-center text-indigo-700">Math Challenge</h1>
      {#if !showNameInput}
        <button 
          on:click={handleStart}
          class="w-full bg-indigo-600 text-white p-3 rounded font-bold hover:bg-indigo-700 transition duration-300 transform hover:scale-105"
        >
          Start
        </button>
      {:else}
        <input
          type="text"
          bind:value={playerName}
          placeholder="Enter your name"
          class="w-full border-2 border-indigo-300 p-2 mb-4 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
        />
        <button 
          on:click={startGame} 
          class="w-full bg-indigo-600 text-white p-3 rounded font-bold hover:bg-indigo-700 transition duration-300 transform hover:scale-105"
          disabled={!playerName.trim()}
        >
          Play
        </button>
      {/if}
    </div>
  {:else if gameStarted}
    <div in:fly="{{ y: 50, duration: 500 }}">
      <h2 class="text-3xl font-bold mb-4 text-center text-indigo-700">{currentQuestion}</h2>
      <input
        type="number"
        bind:value={answer}
        on:keypress={(e) => e.key === 'Enter' && checkAnswer()}
        class="w-full border-2 border-indigo-300 p-2 mb-4 rounded focus:outline-none focus:ring-2 focus:ring-indigo-500 transition"
        placeholder="Your answer"
      />
      <div class="flex justify-between mb-4">
        <p class="text-lg font-semibold">Score: <span class="text-indigo-600">{score}</span></p>
        <p class="text-lg font-semibold">Time: <span class="text-indigo-600">{timeLeft}s</span></p>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
        <div class="bg-indigo-600 h-2.5 rounded-full transition-all duration-500" style="width: {(timeLeft / 90) * 100}%"></div>
      </div>
    </div>
  {:else if gameEnded}
    <div in:fade="{{ duration: 500 }}">
      <h2 class="text-3xl font-bold mb-4 text-center text-indigo-700">Game Over!</h2>
      <p class="text-xl mb-4 text-center">Your score: <span class="font-bold text-indigo-600">{score}</span></p>
      <button 
        on:click={resetGame} 
        class="w-full bg-indigo-600 text-white p-3 rounded font-bold hover:bg-indigo-700 transition duration-300 transform hover:scale-105 mb-6"
      >
        Play Again
      </button>
    </div>
  {/if}

  <div class="mt-8">
    <h3 class="text-2xl font-bold mb-4 text-indigo-700">High Scores</h3>
    <ul class="space-y-2">
      {#each highScores as player, index}
        <li 
          class="bg-indigo-100 p-2 rounded flex justify-between items-center"
          in:fly="{{ y: 50, duration: 300, delay: index * 100 }}"
        >
          <span>{player.name}: <span class="font-bold">{player.score}</span></span>
          <span class="text-sm text-indigo-600">Time: {player.time}s</span>
        </li>
      {/each}
    </ul>
  </div>
</div>
</main>