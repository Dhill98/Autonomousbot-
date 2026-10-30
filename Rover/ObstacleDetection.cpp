#include "ObstacleDetection.h"

bool shouldStop(int distance) {
    if(distance <= 20){
        return true;
    }
    // Example threshold - adjust as needed
    return false;
}