"""Meaningful timing/portability invariants. Test folders are preserved."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO/"skills/yt-edit/scripts"))
import ytlib as y
from projectlib import validate_words,validate_cuts,write_text


class EngineTest(unittest.TestCase):
    def setUp(self):
        self.root=Path(tempfile.mkdtemp(prefix="yt-edit-test-",dir=os.environ.get("YT_EDIT_TEST_DIR")))
        (self.root/"public").mkdir()
        self.config=dict(id="test",title="A neutral example",fps=25,src_dur=10,width=1440,height=1080)
        self.words=[dict(text=t,start=a,end=b) for t,a,b in [('One',.2,.5),('clear',.6,.9),('idea.',1,1.3),('Another',1.4,1.7),('point.',1.8,2.1),('Finish.',8,8.4)]]
        self.save();y.init(self.root)

    def save(self):
        (self.root/"project.json").write_text(json.dumps(self.config))
        (self.root/"transcript.json").write_text(json.dumps(self.words))

    def test_plan_has_no_renderable_side_effect(self):
        y.tag(.2,2,"NOTE",[(.2,"One idea")]);y.plan()
        self.assertTrue((self.root/"plan.md").is_file())
        self.assertFalse((self.root/"public/index.html").exists())

    def test_caption_pages_have_shared_boundary_and_real_word_ids(self):
        markup,pages,times=y._captions()
        self.assertEqual(pages[0][1],pages[1][0])
        self.assertLessEqual(pages[1][1],pages[2][0])
        self.assertEqual(times[0],[.2,.5])
        self.assertIn('class="caption-page clip"',markup[0])
        self.assertIn('id="w0"',markup[0])

    def test_cut_mapping_at_join_and_after_later_cut(self):
        y.init(self.root,cuts=[[2,3],[5,6]])
        self.assertEqual(y.sh(4),3)
        self.assertEqual(y.unsh(2),3)
        self.assertEqual(y.unsh(4),6)
        self.assertEqual(y.P['dur'],8)

    def test_invalid_cuts_fail_before_editing(self):
        for cuts in ([[2,4],[3,5]],[[0,10]],[[3,2]],[[-1,2]]):
            with self.assertRaises(ValueError):validate_cuts(cuts,10)

    def test_invalid_word_times_fail(self):
        for words in ([dict(text='bad',start=2,end=1)],[dict(text='bad',start=float('nan'),end=2)],[]):
            with self.assertRaises(ValueError):validate_words(words,10)

    def test_phrase_anchors_accept_unicode(self):
        self.words=[dict(text='Café',start=.2,end=.5),dict(text='works.',start=.6,end=.9)]
        self.save();y.init(self.root)
        self.assertEqual(y.at('café works'),.2)
        with self.assertRaises(SystemExit):y.at('missing words')

    def test_text_versions_preserve_previous_bytes(self):
        path=self.root/'notes.md';write_text(path,'first');write_text(path,'second');write_text(path,'second')
        self.assertEqual(path.read_text(),'second')
        self.assertEqual((self.root/'notes.previous-1.md').read_text(),'first')
        self.assertFalse((self.root/'notes.previous-2.md').exists())

    def test_wide_and_native_source_geometries(self):
        self.assertEqual(y.ZONES['FULL'],(0,0,1440,1080))
        self.config['width']=1920;self.save();y.init(self.root)
        self.assertEqual(y.ZONES['FULL'],(0,0,1920,1080))
        self.assertGreater(y.ZONES['COL'][0],y.ZONES['SCREEN'][2])

    def test_reinit_clears_prior_cards(self):
        y.tag(.2,2,'NOTE',[(.2,'One idea')]);self.assertTrue(y.CARDS)
        y.init(self.root);self.assertEqual(y.CARDS,[])

    def test_annotation_windows_and_repeated_build_are_stable(self):
        y.pip(3,7,dict(inner='<div>Illustrative screen</div>',label='Example'),[y.note(3,'FIRST','A detail'),y.note(5,'SECOND','Next detail')])
        y.build();first=(self.root/'public/index.html').read_text();y.build()
        self.assertEqual(first,(self.root/'public/index.html').read_text())
        self.assertIn('data-track-index="4"',first)

    def test_theme_rejects_css_injection(self):
        y.P['theme']={'accent':'red;display:none'}
        with self.assertRaises(ValueError):y.build()

    def test_moved_project_uses_no_absolute_source_import(self):
        starter=(REPO/'skills/yt-edit/assets/edit_starter.py').read_text()
        self.assertIn('HERE / "runtime"',starter)
        self.assertNotIn(str(REPO),starter)


if __name__=='__main__':unittest.main()
