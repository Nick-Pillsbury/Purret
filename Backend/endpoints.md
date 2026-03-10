## List of endpoints needed
Use Docker for everything.
1. Front to Master (http)
    - Servo Movement (Up, Down, Left, Right)
    - Camera 
    - Laser
    - Power on, off
    - Starting, Stopping the containers
    - passing up errors
    - (not endpoint but record user id and only allow user to use)
2. Master to Camera 
    - start / stop
    - record
    - health check request
3. Master to Servo
    - movement
    - start / stop
    - health check