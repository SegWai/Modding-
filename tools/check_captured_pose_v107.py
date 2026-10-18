"""Command queue/ack regression checks; no native-engine execution implied."""
from pathlib import Path
import subprocess,tempfile,unittest,re
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'hud-icons-test/MovementLabLocomotion_v106'
TEST=ROOT/'hud-icons-test/MovementLabLocomotion_v107'
W=TEST/'StartGateSource/Scripts/4_World'

class CommandContextTests(unittest.TestCase):
    def test_native_contract_and_only_command_context_writes(self):
        sdk=Path('/tmp/dayz-script-diff/scripts/3_game/dayzplayer.c').read_text()
        self.assertIn('functions usable only from CommandHandler',sdk)
        bridge=(W/'MovementLabCapturedPoseBridge.c').read_text()
        self.assertNotIn('.AnimSetFloat(',bridge)
        actor=(W/'MovementLabConfiguredCorpse.c').read_text()
        start=actor.index('    override void CommandHandler(')
        end=actor.index('    void MovementLabHermitPhysicsCorpse()',start)
        self.assertEqual(actor.count('AnimSetFloat('),1)
        self.assertIn('AnimSetFloat(',actor[start:end])
        self.assertIn('m_CapturedAppliedRevision = m_CapturedRevision;',actor[start:end])
        self.assertIn('!ControlsEvaluated()',bridge)
        self.assertIn('AwaitControlEvaluation();',bridge[bridge.index('m_Phase = 1;'):])

    def test_actual_queue_flush_and_ack_methods(self):
        actor=(W/'MovementLabConfiguredCorpse.c').read_text()
        queue=actor[actor.index('    void QueueCapturedPoseFloat('):actor.index('    void MovementLabHermitPhysicsCorpse()')]
        queue=queue.replace('override void CommandHandler','void CommandHandler')
        queue=queue.replace('        super.CommandHandler(pDt, pCurrentCommandID, pCurrentCommandFinished);','        Guard guard; (void)pDt; (void)pCurrentCommandID; (void)pCurrentCommandFinished;')
        queue=re.sub(r'        if \(m_CapturedAppliedRevision != m_CapturedRevision\)\n            Print\([^\n]+\);\n','',queue)
        bridge=(W/'MovementLabCapturedPoseBridge.c').read_text()
        ack=bridge[bridge.index('    protected void AwaitControlEvaluation()'):bridge.index('    bool Begin(')]
        ack=ack.replace('protected void','void').replace('protected bool','bool').replace('m_Actor.','m_Actor->')
        code=r'''
#include <vector>
#include <map>
#include <cassert>
#include <algorithm>
using namespace std;
bool inCommand=false; int writes=0; map<int,float> nativeValues;
struct Guard { Guard(){assert(!inCommand);inCommand=true;} ~Guard(){inCommand=false;} };
void AnimSetFloat(int id,float v){assert(inCommand);nativeValues[id]=v;writes++;}
template<class T> struct Array:vector<T>{int Find(T v){auto i=find(this->begin(),this->end(),v);return i==this->end()?-1:int(i-this->begin());}void Insert(T v){this->push_back(v);}int Count(){return this->size();}};
struct Actor{Array<int> m_CapturedControlIDs;Array<float> m_CapturedControlValues;int m_CapturedRevision=0,m_CapturedAppliedRevision=0,m_CapturedCommandTicks=0;
QUEUE
};
struct Bridge{Actor* m_Actor;int m_WaitRevision=0,m_AcknowledgedTick=-1;
ACK
};
int main(){
 Actor actor;Bridge bridge{&actor};
 actor.QueueCapturedPoseFloat(100,1);bridge.AwaitControlEvaluation();
 assert(writes==0&&!bridge.ControlsEvaluated()); // scheduled queues never write
 actor.CommandHandler(0,0,false);assert(nativeValues[100]==1);
 assert(!bridge.ControlsEvaluated());assert(!bridge.ControlsEvaluated()); // time alone cannot acknowledge evaluation
 actor.CommandHandler(0,0,false);assert(bridge.ControlsEvaluated());
 for(int i=0;i<546;i++)actor.QueueCapturedPoseFloat(1000+i,float(i)*.001f);
 bridge.AwaitControlEvaluation();assert(!bridge.ControlsEvaluated());
 actor.CommandHandler(0,0,false);assert(!bridge.ControlsEvaluated());
 actor.CommandHandler(0,0,false);assert(bridge.ControlsEvaluated());
 assert(actor.m_CapturedControlIDs.Count()==547&&nativeValues.size()==547);
 for(int i=0;i<546;i++)assert(nativeValues[1000+i]==float(i)*.001f);
 actor.QueueCapturedPoseFloat(100,0);bridge.AwaitControlEvaluation();
 assert(actor.m_CapturedControlIDs.Count()==547&&!bridge.ControlsEvaluated());
 actor.CommandHandler(0,0,false);assert(nativeValues[100]==0&&!bridge.ControlsEvaluated());
 actor.CommandHandler(0,0,false);assert(bridge.ControlsEvaluated());
}
'''.replace('QUEUE',queue).replace('ACK',ack)
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'test.cpp').write_text(code)
            subprocess.run(['g++','-std=c++17','-Wall','-Wextra','-Werror',str(p/'test.cpp'),'-o',str(p/'test')],check=True)
            subprocess.run([str(p/'test')],check=True)

    def test_graph_math_and_other_gameplay_unchanged(self):
        for path in (BASE/'WorkspacePatches').rglob('*'):
            if path.is_file(): self.assertEqual(path.read_bytes(),(TEST/path.relative_to(BASE)).read_bytes())
        for name in ['MovementLabPoseCorrections.c','MovementLabStartGate.c','MovementLabRangeNPC.c']:
            self.assertEqual((BASE/'StartGateSource/Scripts/4_World'/name).read_bytes(),(W/name).read_bytes())
        self.assertEqual((BASE/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_bytes(),(TEST/'Missions/MovementLabMovementLogic.ChernarusPlus/init.c').read_bytes())
        helper=(W/'MovementLabConfiguredCorpse.c').read_text()
        self.assertIn('m_CreatedAt + 350',helper)
        self.assertIn('if (!m_PoseBridge.Step())',helper)
        self.assertIn('positionError <= 0.01 && basisError <= 0.035',(W/'MovementLabCapturedPoseBridge.c').read_text())

if __name__=='__main__':unittest.main(verbosity=2)
