#include <cassert>
#include "../Rover/ObstacleDetection.h"

int main() {
    // Test cases for shouldStop function calls the method directly and sticks a number inside to test.
    assert(shouldStop(10) == true);
    assert(shouldStop(35) == false);
    assert(shouldStop(25) == false);
    assert(shouldStop(20) == true);
    return 0;
}