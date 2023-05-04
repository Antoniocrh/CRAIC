function MOTOrigid16(c3, c2, c1, a5, a4, a3, a2, a1, d3, d2, d1, b5, b4, b3, b2, b1)
    print('RIGIDA,'..a1..','..a2..','..a3..','..a4..','..a5)
    print('RIGIDB,'..b1..','..b2..','..b3..','..b4..','..b5)
    print('RIGIDC,'..c1..','..c2..','..c3)
    print('RIGIDD,'..d1..','..d2..','..d3)
    print('RIGIDE,0,0,0')
    print('RIGEND\n')
end

function MOTOmove19(c3, c2, c1, a5, a4, a3, a2, a1, d3, d2, d1, b5, b4, b3, b2, b1, e3, e2, e1)
    print('MOTORA,'..a1..','..200-a2..','..200-a3..','..a4..','..200-a5)
    print('MOTORB,'..200-b1..','..b2..','..b3..','..200-b4..','..b5)
    print('MOTORC,'..c1..','..c2..','..c3)
    print('MOTORD,'..200-d1..','..200-d2..','..200-d3)
    print('MOTORE,'..e1..','..e2..','..e3)
end

function MOTOmove16(c3, c2, c1, a5, a4, a3, a2, a1, d3, d2, d1, b5, b4, b3, b2, b1)
    print('MOTORA,'..a1..','..200-a2..','..200-a3..','..a4..','..200-a5)
    print('MOTORB,'..200-b1..','..b2..','..b3..','..200-b4..','..b5)
    print('MOTORC,'..c1..','..c2..','..c3)
    print('MOTORD,'..200-d1..','..200-d2..','..200-d3)
end

function MOTOsetspeed(speed)
    print('SPEED '..speed)
end

function MOTOwait()
    print('WAIT\n')
end

function DelayMs(time)
    print('DELAY '..time)
end


