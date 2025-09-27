document.addEventListener("DOMContentLoaded", () => {
  const optionElements = Array.from(document.querySelectorAll(".option"));
  const optionsContainer = document.querySelector(".options");
  const checkButton = document.querySelector('[data-action="check"]');
  const clearButton = document.querySelector('[data-action="clear"]');

  if (!optionElements.length || !optionsContainer) {
    return;
  }

  let selectedOption = null;
  let checked = false;

  const correctOption = optionsContainer.dataset.correct?.trim().toUpperCase();

  function resetStyles() {
    optionElements.forEach((option) => {
      option.classList.remove("selected", "checked", "correct", "incorrect");
    });
  }

  function selectOption(option) {
    if (checked) {
      return;
    }
    resetStyles();
    option.classList.add("selected");
    selectedOption = option.dataset.option;
  }

  function clearSelection() {
    selectedOption = null;
    checked = false;
    resetStyles();
  }

  optionElements.forEach((option) => {
    option.addEventListener("click", () => selectOption(option));
  });

  clearButton?.addEventListener("click", () => {
    clearSelection();
  });

  checkButton?.addEventListener("click", () => {
    if (!selectedOption) {
      optionsContainer.classList.add("shake");
      setTimeout(() => optionsContainer.classList.remove("shake"), 500);
      return;
    }
    checked = true;
    optionElements.forEach((option) => {
      option.classList.remove("selected");
      option.classList.add("checked");
      const isCorrect = option.dataset.option === correctOption;
      if (option.dataset.option === selectedOption) {
        option.classList.add(isCorrect ? "correct" : "incorrect");
      } else if (isCorrect) {
        option.classList.add("correct");
      }
    });
  });
});
