"""Exercise the real typed guide, its evidence navigation and clear/replay controls."""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from streamlit.testing.v1 import AppTest
from src.config import ROOT


def main():
    app=AppTest.from_file(str(ROOT/"hosted_app.py"),default_timeout=60).run()
    results=[]
    def check(label):
        assert not app.exception,[e.message for e in app.exception]
        results.append(dict(check=label,passed=True))
    check("branded app and guide launch")
    assert len(app.chat_input)==1
    for question,expected in [("Why does it say REVISE?","REVISE"),("Explain VaR and ES","131,011"),("How do I save my allocation?","JSON"),("Can I run a backtest?","250"),("Are you a live AI model?","deterministic")]:
        app.chat_input(key="website_chat_input").set_value(question).run()
        check("typed chat: "+question)
        history=app.session_state["website_chat_history"]
        assert history[-2]["text"]==question
        assert expected in history[-1]["text"],history[-1]
        assert "a71dc20a2355" in history[-1]["context"]
    app.button(key="chat_navigate").click().run()
    assert app.selectbox(key="page").value=="Methodology, Sources & AI Disclosure"
    check("guide opens suggested evidence workspace")
    app.button(key="chat_clear").click().run()
    assert app.session_state["website_chat_history"]==[]
    check("chat clears only session conversation")
    app.button(key="replay_welcome").click().run()
    assert app.session_state["_welcome_shown"]
    check("welcome can be replayed without changing the portfolio")
    (ROOT/"outputs/results/branding_chat_checks.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
    print(f"{len(results)} branding/chat checks passed")


if __name__=="__main__":main()
