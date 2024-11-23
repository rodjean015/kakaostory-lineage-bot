#include <Keyboard.h>
#include <Mouse.h>

class Automation {
public:
  // Constructor initializes movement speed and click delay
  Automation(int moveSpeed = 10, int clickDelay = 50)
    : MOVE_SPEED(moveSpeed), CLICK_DELAY(clickDelay) {}

  // Initialize Mouse and Keyboard
  void begin() {
    Serial.begin(9600);
    Mouse.begin();
    Keyboard.begin();
  }

  // Reset Mouse position to the origin
  void resetToOrigin() {
    for (int i = 0; i < 150; i++) {
      Mouse.move(-MOVE_SPEED, -MOVE_SPEED);
      delay(5);
    }
  }

  // Move Mouse in specified direction
  void mouseMove(int xMove, int yMove, int steps, int direction = 1) {
    for (int i = 0; i < steps; i++) {
      Mouse.move(direction * xMove, direction * yMove);
      delay(10);
    }
  }

  // Function to drag the mouse in a specified direction
  void mouseDrag(int xMove, int steps, int holdTime = 10) {
    Mouse.press();
    for (int i = 0; i < steps; i++) {
      Mouse.move(xMove, 0);  // Drag horizontally by xMove
      delay(holdTime);
    }
    Mouse.release();
  }

  // Enter Game action
  void enterGame() {
    mouseMove(11, 6, 70);      // Move to start position
    mouseDrag(5, 10, 50);      // Drag right by 5 pixels for 10 steps
    mouseMove(11, 6, 70, -1);  // Move back to the original position
  }

  // Set Schedule action
  void setSchedule() {
    mouseMove(11, 7, 115);      // Move to schedule position
    Mouse.click();              // Perform click
    mouseMove(11, 7, 115, -1);  // Move back to the original position
  }

  // Click Saving Mode action
  void clickSavingMode() {
    mouseMove(11, 6, 70);      // Move to saving mode position
    Mouse.click();             // Perform click
    mouseMove(11, 6, 70, -1);  // Move back to the original position
  }

  // Click Penalty action
  // void clickPenalty() {
  //   mouseMove(11, 12, 20);      // Move to saving mode position
  //   Mouse.click();             // Perform click
  //   mouseMove(11, 12, 20, -1);  // Move back to the original position
  // }

  // Click Penalty action
  void clickPenalty() {
    mouseMove(11, 12, 60);      // Move to saving mode position
    Mouse.click();             // Perform click
    mouseMove(11, 12, 60, -1);  // Move back to the original position
  }

  void processCommand(const String& command) {
    int cmdCode = -1;

    // Map string commands to integer values
    if (command == "enter_game") cmdCode = 0;
    else if (command == "enter_sched") cmdCode = 1;
    else if (command == "set_sched") cmdCode = 2;
    else if (command == "enter_psm") cmdCode = 3;
    else if (command == "click_psm") cmdCode = 4;
    else if (command == "click_penalty") cmdCode = 5;

    // Switch-case for different commands
    switch (cmdCode) {
      case 0:  // enter_game
        enterGame();
        delay(5000);
        clickPenalty();
        delay(5000);
        Keyboard.press('z');
        delay(100);
        Keyboard.release('z');
        delay(5000);
        setSchedule();
        delay(100);
        setSchedule();
        mouseMove(10, 4, 20);
        delay(30000);
        Keyboard.press('q');
        delay(100);
        Keyboard.release('q');
        delay(30000);
        resetToOrigin();
        clickSavingMode();
        break;
      case 1:  // enter_sched
        mouseMove(10, 4, 20);
        Mouse.click();
        Keyboard.press('z');
        delay(100);
        Keyboard.release('z');
        break;
      case 2:  // set_sched
        setSchedule();
        break;
      case 3:  // enter_psm
        mouseMove(10, 4, 20);
        Mouse.click();
        Keyboard.press('q');
        delay(100);
        Keyboard.release('q');
        break;
      case 4:  // click_psm
        clickSavingMode();
        break;
      case 5:  // click_psm
        clickPenalty();
        break;
      default:  // No matching command
        break;
    }

    Keyboard.releaseAll();
  }

  // End Mouse and Keyboard operations
  void end() {
    Mouse.end();
    Keyboard.end();
  }

private:
  const int MOVE_SPEED;
  const int CLICK_DELAY;
};

// Create an instance of Automation
Automation automation;

void setup() {
  automation.begin();
}

void loop() {
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    Serial.print("Received command: ");
    Serial.println(command);

    automation.resetToOrigin();
    automation.processCommand(command);
  }
}