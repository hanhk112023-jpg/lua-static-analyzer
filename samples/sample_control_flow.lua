-- Sample 4: Dispatcher Loop with State Transitions (Simulated Flattened CFG)
local state = 1
while state do
    if state <= 2 then
        if state <= 1 then
            print("Step 1: Init")
            state = 2
        else
            print("Step 2: Processing")
            state = 3
        end
    else
        if state <= 3 then
            print("Step 3: Finalizing")
            state = 4
        else
            print("Completed")
            state = nil
        end
    end
end
