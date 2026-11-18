# One Day, the Whole World — Wednesday 18 November 2026

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/yula3070/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/yula3070/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

Thirty-five stories from six continents on a single front page: the Gulf
flares again, a span of the Kerch bridge falls into the sea, and Trump
meets the Quad in Manila before flying to Shenzhen for APEC.

## What is on the page

- **3 lead stories**, each with its own flat-vector illustration: the
  US–Iran exchange over Bahrain and Qeshm Island, the Kerch bridge span,
  and the Quad summit in Manila.
- **6 middle stories**, each with its own icon: Nvidia's $115.8bn quarter,
  Cyclone Akvan, the Knesset electing Kahana 66–52, the EU's €45bn Ukraine
  loan, Wall Street's fourth straight fall, and APEC opening in Shenzhen.
- **A dotted world map** with numbered pins marking stories 1–9.
- **BY THE NUMBERS**: 66–52, $115.8bn, 145 km/h, 204,070.
- **ALSO**: 26 more stories from the day, numbered 10–35.

## How it was built

`draw_frontpage.py` draws the whole page with PIL — every picture is a
flat vector shape drawn in that file. No photos, no copied art.

```sh
python3 draw_frontpage.py   # writes entry.png (1024x1024, deterministic)
```

## Sources

Every story on the page happened, or was first reported, on Wednesday
18 November 2026. Reporting: Reuters, AP, Al Jazeera, BBC, CNN, IMD,
NASA, UN. Disputed claims are attributed to their source.

## License

MIT — see `LICENSE`.
