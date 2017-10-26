--[[ 
    公共函数封装
]]--




--功能名称： 点击屏幕。
--功能描述： 根据输入坐标，点击屏幕。
--输入数据结构：（X,Y）坐标
--返回数据结构： Booleans
function tapScreen(x,y)
		touchDown(0, x, y);
    mSleep(200);
    touchUp(0, x, y);
		return true
end




--功能名称： 点击屏幕。
--功能描述： 根据输入坐标，增加/减少随机数后点击屏幕。
--输入数据结构：（X,Y）坐标
--返回数据结构： Booleans
function tapScreenRandom(x, y)
    local x,y = x,y
		math.randomseed(tostring(os.time()):reverse():sub(1, 6))    --设置随机数种子
		local index = math.random(1,5)
		x = x + math.random(-5,5)    --真实坐标最大差值为5
		y = y + math.random(-5,5)
		touchDown(index,x,y)
		mSleep(math.random(80,180))    --某些情况需要增大延迟才能模拟点击效果
		touchUp(index,x,y)
		return true
end




--功能名称： 划动屏幕。
--功能描述： 根据输入坐标组，划动屏幕。(注： 适用范围 100 ~ 400)
--输入数据结构： (X,Y,toX,toY) 坐标组
--返回数据结构： Booleans
function moveScreen(x,y,toX,toY)
    touchDown(1, x, y);    --ID为1的手指在 (x, y) 按下
		mSleep(50);
		touchMove(1, toX, toY);    --移动到 (toX, toY)
		mSleep(50);
		touchUp(1, toX, toY);    --在(toX, toY) 抬起
    return true
end




--功能名称： 划动屏幕。(注： 未完成)
--功能描述： 根据输入坐标组，根据距离比例分单次、多次滑动，相应增加/减少随机数。
--输入数据结构： (X,Y,toX,toY) 坐标组
--返回数据结构： Booleans
--function moveScreenRandom(x,y,toX,toY)
--    local x,y,toX,toY = x,y,toX,toY
--		local xLength = toX - x
--		local yLength = toY - y
--		math.randomseed(tostring(os.time()):reverse():sub(1, 6))    --设置随机数种子
--		local index = math.random(1,5)
--		local moveLength =  math.random(100,250)    --移动距离
		
--		if xLength == 0 then
--		    local remainder = yLength%moveLength    --移动余数距离
--		    local moveTimes = ((remainder == 0) and {yLength/moveLength} or {(yLength/moveLength) + 1})[1]     -- 移动次数
				
--				x = x + math.random(-10,10)    --真实坐标最大差值为10
--		    y = y + math.random(-10,10)    
--				toX = toX + math.random(-10,10)     
--		    toY = toy + math.random(-10,10) 
				
--		else if yLength == 0 then
		
--		else
--			return false
--		end
--end




--功能名称： 获取屏幕方向。
--功能描述： 获取化操作系统，获取屏幕方向。
--function getScreenDirection()
--		osType = getOSType()
--		screenDirection = getScreenDirection()
		
--end

