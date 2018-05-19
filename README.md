# NFL Coordinator matchups - Offensive vs Defensive Coordinators

This work was created on the back of conversations between members of the <a id="effllink" href="https://allybhoy.wordpress.com/">Earlston Fantasy Football League</a> community. We posed the hypothesis

>”Do offensive coordinators change what they do against certain defenses?"

Anecdotally this appeared to be the case, one only has to look at the New England Patriots offense as a prime example of a coordinator and philosophy that seems to change on a game by game basis.

From this starting point we a little deeper by extracting NFL play by play data using the excellent <a id="nfldblink" href="https://github.com/BurntSushi/nfldb">nfldb</a> to produce play by play data for each offensive and defensive coordinator from 2012 - 2017. At first we concentrated on individual matchups, but, unfortunately job security among NFL coaches isn't great. This meant we were working, at best, with very limited sample size or more likely no data. This led us to classifying offenses and defenses (at a very simple level) by coaching tree or style. This allowed us to fill holes with more generic matchups and also look at making predictions for new coordinators.

This repo holds the python code to create and extract your own version. The data and results are presented in <a id="studiolink" href="https://datastudio.google.com/reporting/1btImS_YJxkKMXdeL0xYcWmV8R1DBTxzo/page/iV8P/edit">google studio</a>

Can you help? If you classify offenses and defenses then we'd love to work with you.

![scatter](/image.png)
