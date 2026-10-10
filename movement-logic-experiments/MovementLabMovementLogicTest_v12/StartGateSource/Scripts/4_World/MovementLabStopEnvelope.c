// Shared by ordinary sprint release and forced direction-change braking.
class MovementLabStopEnvelope
{
    static float Sprint(float start, float fraction)
    {
        if (fraction < 0.18)
        {
            float sprintBlend = Math.Clamp(fraction / 0.18, 0, 1);
            sprintBlend = 2.0 * sprintBlend - sprintBlend * sprintBlend;
            return start + (2.0 - start) * sprintBlend;
        }
        if (fraction < 0.82)
        {
            // Smoothly traverse jog -> walk, without v11's fixed-speed holds.
            float jogBlend = Math.Clamp((fraction - 0.18) / 0.64, 0, 1);
            jogBlend = jogBlend * jogBlend * (3.0 - 2.0 * jogBlend);
            return 2.0 - jogBlend;
        }
        float walkBlend = Math.Clamp((fraction - 0.82) / 0.18, 0, 1);
        walkBlend = walkBlend * walkBlend * (3.0 - 2.0 * walkBlend);
        return 1.0 - walkBlend;
    }
}
