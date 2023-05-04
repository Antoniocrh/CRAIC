

dofile('0:/lua/lib.lua')
dofile('0:/lua/Actionlib.lua')


while(true)
do
    actname = req_actionLUA()

    if actname == 'default' then
        DelayMs(1)
    elseif actname == -255 then
        act_errorLUA()
    else
        act_startLUA()
        fun =_G[actname]
        fun()
        act_completeLUA()
    end
    
end
-- 以上程序不允许修改


