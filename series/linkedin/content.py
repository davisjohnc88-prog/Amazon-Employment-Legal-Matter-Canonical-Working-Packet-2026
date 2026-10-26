# A standalone LinkedIn document post: the bird's-eye view, focused on bullying, system manipulation,
# and how the moves were handed down. Build it with series/build/build.py and SERIES_CONTENT=<this file>.
#
# Whose words are whose:
#   echo titles and history lines  -> the On the Bus or Off the Bus timeline (fact-checked), trimmed but not reworded
#   "from my report" quotes        -> John Charles's report, word for word ("the author's" becomes "my")
#   term, definition, at-work line -> the report's Part XV field guide, word for word (except slide 6's at-work line)
#   slides reused from batch 01     -> copied from series/build/content.py, already checked
#   cover, kickers, slide 6 work line, CTA -> drafted by Claude to tie it together; edit freely
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build"))
import content as B1

SERIES = B1.SERIES
SINGLES, POSTER_TERMS = [], []


def b1(slug, i):
    """A slide from batch 01, unchanged."""
    return dict(next(c for c in B1.CAROUSELS if c["slug"] == slug)["slides"][i])


def echo(year, img, title, hist, term, define, work, source, rq=None, lab="The same move at work"):
    return {"type": "echo", "img": img, "kicker": f"History echo · {year}", "title": title, "hist": hist, "rq": rq,
            "lab": lab, "term": term, "def": define, "work": work, "source": source}


whole_map = b1("00-the-whole-map", 0)
stat = b1("03-by-the-numbers", 5)
stat.update(kicker="Who gets targeted", body=b1("00-the-whole-map", 5)["body"])

CAROUSELS = [{
    "slug": "linkedin-the-playbook-was-handed-down",
    "title": "Workplace bullying didn't invent its moves. It inherited them.",
    "slides": [
        {"type": "cover", "img": "map-string",
         "kicker": "The bird's-eye view",
         "title": "Workplace bullying didn't invent its moves.<br><em>It inherited them.</em>",
         "sub": "Four hundred years of sorting people, and the playbook it left at work."},
        b1("00-the-whole-map", 3),
        {"type": "quote", "kicker": "From my report",
         "quote": "A eugenics board needed a label, a record, and an audience that would not believe the person being labeled.",
         "line": "So does a workplace mob.",
         "body": "<p>The narcissistic and bullying tactics in my vocabulary are not a separate subject from the history of human sorting. They are the interpersonal version of it.</p>",
         "by": "John Charles Davis · <em>On the Bus or Off the Bus</em>"},
        echo("1912", "paper-stacks", "“Deborah Kallikak” was Emma Wolverton",
             "Goddard's <em>The Kallikak Family</em> makes a pedigree argument out of a real woman, Emma Wolverton. She lived 81 of her 89 years in institutions.",
             "Credibility laundering", "Reputation damaged in advance so later reports are not believed.",
             "A story about you that reaches the room before you do.",
             "Embryo Project Encyclopedia, Arizona State University"),
        echo("1917", "shadow-maze", "Army Alpha and Beta",
             "About 1.75 million recruits take Robert Yerkes's tests. Carl Brigham's 1923 book uses the results to rank national groups. He recants in 1930.",
             "The invisible standard", "An unspoken expectation that works as a gate.",
             "“Culture fit”; eye contact as a hiring test.",
             "EBSCO Research Starters, “Intelligence Testing and Immigration Legislation”",
             rq="Many items rewarded familiarity with American culture rather than reasoning."),
        echo("1949", "kitchen-dough", "“Refrigerators which did not defrost”",
             "Kanner describes the children as kept “neatly in refrigerators which did not defrost.” The metaphor gets away from him. Bettelheim's <em>The Empty Fortress</em> (1967) turns it into mother-blame.",
             "The burden shift", "A systemic problem moved onto the individual.",
             "The “problem employee” carries the blame, so the system never has to change.",
             "Autism History Project, University of Oregon"),
        echo("1961", "finish-lines", "The borderline line, drawn at 85",
             "The American Association on Mental Deficiency defines subaverage intelligence as IQ below about 85. In 1973 it moves the line to about 70. Roughly 14% of people, scoring between 70 and 85, move out of the category without anyone changing.",
             "Moving the goalposts", "Changing the standard after it is met.",
             "Targets raised the month you hit them.",
             "<em>Parallels in Time</em>, Minnesota Governor's Council on Developmental Disabilities"),
        {"type": "grid2", "kicker": "From my field guide",
         "title": "One playbook, two halves",
         "cols": [
             ("Person to person", [
                 ("Mobbing", "A whole team cooling toward one person at once."),
                 ("DARVO", "Reporting harassment and being investigated for your “conduct.”"),
                 ("Triangulation", "“Leadership is concerned.” “Everyone has noticed.”"),
                 ("Tone policing", "“This would land better if you were calmer.”"),
             ]),
             ("Built into the system", [
                 ("Strategic vagueness", "“Be more of a team player,” never defined."),
                 ("Plausible deniability", "“The system flagged you, not me.”"),
                 ("Documentation asymmetry", "A file you did not know existed."),
                 ("Hope as a retention tool", "“The next review cycle will be better.”"),
             ]),
         ],
         "source": "Examples from my report's field guide. DARVO is Jennifer Freyd's research term; mobbing is Heinz Leymann's."},
        b1("03-by-the-numbers", 3),
        stat,
        b1("01-youre-not-crazy", 8),
        echo("1966", "archive", "Christmas in Purgatory",
             "Burton Blatt and photographer Fred Kaplan publish hidden-camera photos of back wards at five state institutions.",
             "Keep your own record", "The institution has the file; you do not.",
             "Dated notes, saved messages, and copies of your own requests are a modest counterweight. They are not paranoia. They are the file you would otherwise not have.",
             "Syracuse University Archives, Burton Blatt Papers",
             rq="The institutions were exposed by people who carried cameras inside.", lab="What the history asks"),
        {"type": "cta", "img": "desk-journal",
         "kicker": "Read the whole map",
         "title": "The history, the vocabulary, and my story",
         "body": "Long-form on Substack, with every source listed.",
         "foot": "Link in the first comment. Save this, and send it to someone who needs to hear they're not crazy."},
    ],
}]
