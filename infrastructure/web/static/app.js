const state = {
  roomNumber: null,
  playerId: null,
  game: null,
  mode: "flip",
  selectedHandIndex: null,
  selectedCourtIndex: null,
  pendingSelections: [],
  pollTimer: null,
  winnerModalShown: false,
};

const joinView = document.getElementById("join-view");
const waitView = document.getElementById("wait-view");
const gameView = document.getElementById("game-view");
const roomInput = document.getElementById("room-input");
const joinBtn = document.getElementById("join-btn");
const joinStatus = document.getElementById("join-status");
const waitStatus = document.getElementById("wait-status");
const turnBanner = document.getElementById("turn-banner");
const turnPill = document.getElementById("turn-pill");
const deckPill = document.getElementById("deck-pill");
const opponentPill = document.getElementById("opponent-pill");
const messagePill = document.getElementById("message-pill");
const courtCards = document.getElementById("court-cards");
const myHand = document.getElementById("my-hand");
const modeFlipBtn = document.getElementById("mode-flip");
const modeSwapBtn = document.getElementById("mode-swap");
const selectionStatus = document.getElementById("selection-status");
const validateBtn = document.getElementById("validate-btn");
const pendingPanel = document.getElementById("pending-panel");
const pendingText = document.getElementById("pending-text");
const pendingActions = document.getElementById("pending-actions");
const privateStatus = document.getElementById("private-status");
const peekModal = document.getElementById("peek-modal");
const peekModalCards = document.getElementById("peek-modal-cards");
const peekModalClose = document.getElementById("peek-modal-close");

peekModalClose.addEventListener("click", () => peekModal.close());

const visibilityModal = document.getElementById("visibility-modal");
document.getElementById("visibility-hidden").addEventListener("click", () => submitSwap(false));
document.getElementById("visibility-visible").addEventListener("click", () => submitSwap(true));

async function submitSwap(visible) {
  visibilityModal.close();
  await submitAction({
    type: "swap_hand_court",
    hand_index: state.selectedHandIndex,
    court_index: state.selectedCourtIndex,
    visible,
  });
  state.selectedHandIndex = null;
  state.selectedCourtIndex = null;
  renderHands();
  renderCourt();
}

const winModal = document.getElementById("win-modal");
const winModalIcon = document.getElementById("win-modal-icon");
const winModalTitle = document.getElementById("win-modal-title");
const winModalStrategy = document.getElementById("win-modal-strategy");
const winModalDesc = document.getElementById("win-modal-desc");
const winModalReplay = document.getElementById("win-modal-replay");

winModalReplay.addEventListener("click", playAgain);

joinBtn.addEventListener("click", connectRoom);
modeFlipBtn.addEventListener("click", () => setMode("flip"));
modeSwapBtn.addEventListener("click", () => setMode("swap"));
validateBtn.addEventListener("click", validateAction);

function setMode(mode) {
  state.mode = mode;
  state.selectedHandIndex = null;
  state.selectedCourtIndex = null;
  renderModeButtons();
  renderSelectionStatus();
  renderCourt();
  renderHands();
}

function renderModeButtons() {
  modeFlipBtn.classList.toggle("active", state.mode === "flip");
  modeSwapBtn.classList.toggle("active", state.mode === "swap");
}

function switchView(view) {
  joinView.classList.add("hidden");
  waitView.classList.add("hidden");
  gameView.classList.add("hidden");
  view.classList.remove("hidden");
}

async function connectRoom() {
  const roomNumber = Number(roomInput.value);
  joinStatus.textContent = "Connecting...";

  const res = await fetch("/api/rooms/connect", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ room_number: roomNumber }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    joinStatus.textContent = data.detail || "Could not connect";
    return;
  }

  const data = await res.json();
  state.roomNumber = data.room_number;
  state.playerId = data.player_id;

  if (!data.ready) {
    switchView(waitView);
    waitStatus.textContent = `Connected as player ${state.playerId + 1}.`;
    await waitForOpponent();
    return;
  }

  await enterGame();
}

async function waitForOpponent() {
  clearPolling();
  state.pollTimer = setInterval(async () => {
    const res = await fetch(`/api/rooms/${state.roomNumber}/status`);
    if (!res.ok) return;
    const data = await res.json();
    waitStatus.textContent = `Players connected: ${data.players_connected}/2`;
    if (data.ready) {
      clearPolling();
      await enterGame();
    }
  }, 900);
}

async function enterGame() {
  switchView(gameView);
  await fetchState();
  setMode("flip");
  clearPolling();
  state.pollTimer = setInterval(fetchState, 800);
}

function clearPolling() {
  if (state.pollTimer) {
    clearInterval(state.pollTimer);
    state.pollTimer = null;
  }
}

async function fetchState() {
  if (state.roomNumber == null || state.playerId == null) return;

  const res = await fetch(`/api/rooms/${state.roomNumber}/state/${state.playerId}`);
  if (!res.ok) {
    messagePill.textContent = "Status: Failed to fetch game state";
    return;
  }

  state.game = await res.json();
  // Clear pending selections when it's no longer our turn
  if (!state.game.is_my_turn) {
    state.selectedHandIndex = null;
    state.selectedCourtIndex = null;
  }
  renderGame();
}

function renderGame() {
  renderStatus();
  renderCourt();
  renderHands();
  renderPending();
  renderSelectionStatus();

  if (state.game.winner && !state.winnerModalShown) {
    state.winnerModalShown = true;
    clearPolling();
    showWinModal(state.game.winner);
  }
}

function renderStatus() {
  if (!state.game) return;
  const turnLabel = state.game.is_my_turn ? "Your turn" : "Opponent turn";
  turnPill.textContent = `Turn: ${turnLabel}`;
  turnBanner.textContent = state.game.is_my_turn ? "YOUR TURN" : "OPPONENT TURN";
  turnBanner.classList.toggle("my-turn", state.game.is_my_turn);
  turnBanner.classList.toggle("opponent-turn", !state.game.is_my_turn);
  deckPill.textContent = `Deck: ${state.game.deck_count}`;
  opponentPill.textContent = `Opponent cards: ${state.game.opponent_hand_count}`;
  messagePill.textContent = `Status: ${state.game.message || "-"}`;

  const controlsEnabled = state.game.is_my_turn && !state.game.winner;
  modeFlipBtn.disabled = !controlsEnabled;
  modeSwapBtn.disabled = !controlsEnabled;

  const canValidate = controlsEnabled && !state.game.pending_effect &&
    (state.mode === "flip" ? state.selectedCourtIndex != null
      : state.selectedHandIndex != null && state.selectedCourtIndex != null);
  validateBtn.disabled = !canValidate;
}

function renderCourt() {
  if (!state.game) return;
  courtCards.innerHTML = "";
  const controlsEnabled = state.game.is_my_turn && !state.game.winner;
  state.game.court_cards.forEach((card, index) => {
    const button = document.createElement("button");
    button.className = `game-card ${card.name === "Hidden" ? "hidden-card" : ""} selectable`;
    const courtPendingEffects = ["assassin_peek", "knight_swap", "knight_flip", "king_flip"];
    const isCourtPendingSelected = courtPendingEffects.includes(state.game.pending_effect?.type)
      && state.pendingSelections.includes(index);
    if (state.selectedCourtIndex === index || isCourtPendingSelected) {
      button.classList.add("selected");
    }
    button.textContent = card.name;
    button.disabled = !controlsEnabled;
    if (!controlsEnabled) {
      button.classList.add("disabled-card");
    }
    button.addEventListener("click", () => onCourtCardClick(index));
    courtCards.appendChild(button);
  });
}

function renderHands() {
  if (!state.game) return;
  myHand.innerHTML = "";
  const controlsEnabled = state.game.is_my_turn && !state.game.winner;
  state.game.my_hand.forEach((card, index) => {
    const button = document.createElement("button");
    button.className = "game-card selectable";
    const isHandPendingSelected = state.game.pending_effect?.type === "king_discard" && state.pendingSelections.includes(index);
    if ((state.mode === "swap" && state.selectedHandIndex === index) || isHandPendingSelected) {
      button.classList.add("selected");
    }
    button.textContent = card.name;
    button.disabled = !controlsEnabled;
    if (!controlsEnabled) {
      button.classList.add("disabled-card");
    }
    button.addEventListener("click", () => onMyHandClick(index));
    myHand.appendChild(button);
  });
}

async function onCourtCardClick(index) {
  if (!state.game.is_my_turn || state.game.winner) return;

  if (state.game.pending_effect) {
    handlePendingSelection(index);
    return;
  }

  state.selectedCourtIndex = state.selectedCourtIndex === index ? null : index;
  renderCourt();
  renderSelectionStatus();
  renderStatus();
}

async function validateAction() {
  if (!state.game || !state.game.is_my_turn || state.game.pending_effect) return;

  if (state.mode === "flip" && state.selectedCourtIndex != null) {
    await submitAction({ type: "flip_court", court_index: state.selectedCourtIndex });
    state.selectedCourtIndex = null;
    return;
  }

  if (state.mode === "swap" && state.selectedHandIndex != null && state.selectedCourtIndex != null) {
    visibilityModal.showModal();
    return;
  }
}

function onMyHandClick(index) {
  if (!state.game || !state.game.is_my_turn) return;

  if (state.game.pending_effect?.type === "king_discard") {
    handlePendingSelection(index);
    return;
  }

  if (state.mode !== "swap" || state.game.pending_effect) return;

  state.selectedHandIndex = state.selectedHandIndex === index ? null : index;
  renderHands();
  renderSelectionStatus();
}

function renderSelectionStatus() {
  if (!state.game) return;
  if (!state.game.is_my_turn) {
    selectionStatus.textContent = "Wait for opponent move.";
    return;
  }
  if (state.game.pending_effect) {
    selectionStatus.textContent = "Resolve pending effect.";
    return;
  }
  if (state.mode === "flip") {
    if (state.selectedCourtIndex == null) {
      selectionStatus.textContent = "Click a court card to select it, then Validate.";
    } else {
      selectionStatus.textContent = `Court card ${state.selectedCourtIndex + 1} selected. Click Validate to flip.`;
    }
    return;
  }
  if (state.selectedHandIndex == null) {
    selectionStatus.textContent = "Select one card from your hand, then a court card, then Validate.";
    return;
  }
  if (state.selectedCourtIndex == null) {
    selectionStatus.textContent = `Hand card ${state.selectedHandIndex + 1} selected. Now pick a court card.`;
    return;
  }
  selectionStatus.textContent = `Hand card ${state.selectedHandIndex + 1} ↔ Court card ${state.selectedCourtIndex + 1}. Click Validate to swap.`;
}

function renderPending() {
  pendingActions.innerHTML = "";
  privateStatus.textContent = "";

  if (!state.game.pending_effect || !state.game.is_my_turn) {
    pendingPanel.classList.add("hidden");
    state.pendingSelections = [];
    return;
  }

  pendingPanel.classList.remove("hidden");
  const type = state.game.pending_effect.type;

  if (type === "assassin_peek") {
    pendingText.textContent = "Pick 2 court cards, then submit.";
    addPendingSubmitButton("Submit peek", () => {
      if (state.pendingSelections.length !== 2) return;
      const sorted = state.pendingSelections.slice().sort((a, b) => a - b);
      submitAction({ type: "assassin_peek", indices: sorted });
    });
    return;
  }

  if (type === "knight_swap") {
    pendingText.textContent = "Pick 2 court cards to swap, then submit.";
    addPendingSubmitButton("Submit swap", () => {
      if (state.pendingSelections.length !== 2) return;
      submitAction({
        type: "knight_swap",
        first_index: state.pendingSelections[0],
        second_index: state.pendingSelections[1],
      });
    });
    return;
  }

  if (type === "knight_flip") {
    pendingText.textContent = "Pick 1 court card to flip (no effect).";
    addPendingSubmitButton("Submit flip", () => {
      if (state.pendingSelections.length !== 1) return;
      submitAction({ type: "knight_flip", court_index: state.pendingSelections[0] });
    });
    return;
  }

  if (type === "queen_peek") {
    pendingText.textContent = "Pick 2 opponent hand slots, then submit.";
    [0, 1, 2].forEach((idx) => {
      const btn = document.createElement("button");
      const isSelected = state.pendingSelections.includes(idx);
      btn.className = `btn btn-secondary${isSelected ? " active" : ""}`;
      btn.textContent = `Slot ${idx + 1}`;
      btn.addEventListener("click", () => togglePendingIndex(idx, 2));
      pendingActions.appendChild(btn);
    });
    addPendingSubmitButton("Submit queen", () => {
      if (state.pendingSelections.length !== 2) return;
      submitAction({ type: "queen_peek", indices: state.pendingSelections.slice(0, 2) });
    });
    return;
  }

  if (type === "king_choice") {
    pendingText.textContent = "Choose king mode.";
    addPendingSubmitButton("Flip mode", () => submitAction({ type: "king_choice", mode: "flip" }));
    addPendingSubmitButton("Draw mode", () => submitAction({ type: "king_choice", mode: "draw" }));
    return;
  }

  if (type === "king_flip") {
    pendingText.textContent = "Pick 1 court card to flip and trigger.";
    addPendingSubmitButton("Submit king flip", () => {
      if (state.pendingSelections.length !== 1) return;
      submitAction({ type: "king_flip", court_index: state.pendingSelections[0] });
    });
    return;
  }

  if (type === "king_discard") {
    pendingText.textContent = "Pick 2 of your hand cards to discard, then submit.";
    addPendingSubmitButton("Submit discard", () => {
      if (state.pendingSelections.length !== 2) return;
      submitAction({ type: "king_discard", indices: state.pendingSelections.slice(0, 2) });
    });
    return;
  }

  pendingText.textContent = "Unknown pending effect.";
}

function addPendingSubmitButton(label, handler) {
  const btn = document.createElement("button");
  btn.className = "btn btn-secondary";
  btn.textContent = label;
  btn.addEventListener("click", handler);
  pendingActions.appendChild(btn);
}

function handlePendingSelection(index) {
  const type = state.game.pending_effect?.type;
  if (!type) return;

  if (type === "assassin_peek" || type === "knight_swap") {
    togglePendingIndex(index, 2);
    return;
  }

  if (type === "knight_flip" || type === "king_flip") {
    state.pendingSelections = [index];
    selectionStatus.textContent = `Selected index ${index + 1}`;
    renderCourt();
    return;
  }

  if (type === "king_discard") {
    togglePendingIndex(index, 2);
  }
}

function togglePendingIndex(index, maxCount) {
  const current = state.pendingSelections;
  const found = current.indexOf(index);
  if (found >= 0) {
    current.splice(found, 1);
  } else if (current.length < maxCount) {
    current.push(index);
  }
  selectionStatus.textContent = `Pending picks: ${current.map((n) => n + 1).join(", ") || "none"}`;
  renderCourt();
  renderHands();
  renderPending();
}

const STRATEGY_LABELS = {
  wedding: { name: "Wedding Victory", desc: "3 Queens united — love conquers all." },
  coronation: { name: "Coronation", desc: "3 Kings gathered — the throne is yours." },
  assassination: { name: "Assassination", desc: "2 Assassins eliminated their target." },
};

function showWinModal(winner) {
  const isMine = winner.player_id === state.playerId;
  const strategy = STRATEGY_LABELS[winner.reason] ?? { name: winner.reason, desc: "" };

  winModalIcon.textContent = isMine ? "👑" : "💀";
  winModalTitle.textContent = isMine ? "Victory!" : "Defeat";
  winModalStrategy.textContent = strategy.name;
  winModalDesc.textContent = strategy.desc;
  winModal.classList.toggle("win-modal--victory", isMine);
  winModal.classList.toggle("win-modal--defeat", !isMine);
  winModal.showModal();
}

async function playAgain() {
  const res = await fetch(`/api/rooms/${state.roomNumber}/reset`, { method: "POST" });
  if (!res.ok) {
    winModal.close();
    return;
  }
  state.game = null;
  state.winnerModalShown = false;
  state.selectedHandIndex = null;
  state.selectedCourtIndex = null;
  state.pendingSelections = [];
  winModal.close();
  await fetchState();
  clearPolling();
  state.pollTimer = setInterval(fetchState, 800);
}

function showPeekModal(cardNames) {
  peekModalCards.innerHTML = "";
  cardNames.forEach((name) => {
    const div = document.createElement("div");
    div.className = "game-card peek-modal__card";
    div.textContent = name;
    peekModalCards.appendChild(div);
  });
  peekModal.showModal();
}

async function submitAction(action) {
  const res = await fetch(`/api/rooms/${state.roomNumber}/action`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      player_id: state.playerId,
      action,
    }),
  });

  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    selectionStatus.textContent = data.detail || "Action failed";
    return;
  }

  const data = await res.json();
  state.pendingSelections = [];

  if (data.result?.private) {
    const cards = data.result.private.peeked_cards ?? data.result.private.revealed_cards;
    if (cards?.length) {
      showPeekModal(cards);
    }
  }

  if (!data.result.ok) {
    selectionStatus.textContent = data.result.message || "Invalid action";
  } else {
    selectionStatus.textContent = data.result.message || "Action applied";
  }

  state.game = data.state;
  renderGame();
}

setMode("flip");
