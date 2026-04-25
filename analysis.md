# Analysis

## 1. Which city has the highest inefficiency ratio? What cables serve it and how does that explain your result?

    The city that had the highest inefficiency ratio was London with a ratio of 2.95. Though London is one of the closer cities to Boston geographically, the measured RTT was much higher than the theoretical minimum, which shows real Internet traffic doesn't travel in a straight line. 
    
    According to submarinecablemap.com, the Bay of London is served by the R100 North Cable. This indicates that London has access to submarine cable infrastructure, but cable access alone does not guarantee minimum latency. Packets must still travel through inland fiber routes, routers, Internet exchange points, and provider peering networks before reaching the destination. Congestion and indirect routing decisions can also increase RTT.

---

## 2. Which city is closest to the theoretical minimum? What does that tell you about routing infrastructure there?

    The city closest to the theoretical minimum was Sydney, with a ratio of 1.01. Singapore was also very close with a ratio of 1.02. This suggests that the routes to Sydney and Singapore are highly optimized. It also shows that long distance alone does not always create poor latency; strong infrastructure and direct routing can make distant cities perform efficiently.

---

## 3. Your packet to Lagos almost certainly routes through Europe first. Why does Africa route through Europe, and what would need to change to fix it?

    The RTT to Lagos had an inefficiency ratio of 2.03, which shows the route was probably not direct. Many Internet connections in Africa were built to connect through Europe since European carriers developed submarine cable systems and exchange hubs earlier than many African regions. Because of this, traffic between Africa and North America may pass through London, Lisbon, or another European hub first before reaching its final destination, which increases path length adding delay.

    To improve this, more direct connectivity would be needed, including:
        - More Africa-to-America submarine cables  
        - Stronger regional Internet Exchange Points (IXPs) in Africa  
        - More local peering between African networks  
        - Mored data centers and cloud infrastructures in Africa 