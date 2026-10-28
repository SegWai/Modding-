class ML158DemoCycle
{
 static float Target(int poseIndex)
 {
  if (poseIndex == 0)
   return -1;
  if (poseIndex == 2)
   return 1;
  return 0;
 }
};
