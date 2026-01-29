pub struct AudioConfig {
    pub sample_rate: u32,
    pub channels: u16,
}

pub struct DspPipeline {
    _config: AudioConfig,
    noise_profile: Vec<f32>,
    echo_buffer: Vec<f32>,
    peak_level: f32,
}

impl DspPipeline {
    pub fn new(config: AudioConfig) -> Self {
        Self {
            _config: config,
            noise_profile: vec![0.0; 512],
            echo_buffer: vec![0.0; 4096],
            peak_level: 0.0,
        }
    }

    pub fn process(&mut self, buffer: &mut [f32]) {
        self.suppress_noise(buffer);
        self.cancel_echo(buffer);
        self.normalize_gain(buffer);
    }

    fn suppress_noise(&mut self, buffer: &mut [f32]) {
        const ALPHA: f32 = 1.5;
        const BETA: f32 = 0.01;

        for (i, sample) in buffer.iter_mut().enumerate() {
            let noise = self.noise_profile[i % self.noise_profile.len()];
            let suppressed = sample.abs() - (ALPHA * noise);
            let suppressed = suppressed.max(BETA * sample.abs());
            
            *sample = if *sample >= 0.0 { suppressed } else { -suppressed };
        }
    }

    fn cancel_echo(&mut self, buffer: &mut [f32]) {
        const MU: f32 = 0.1;

        for (i, sample) in buffer.iter_mut().enumerate() {
            if i < self.echo_buffer.len() {
                let input = *sample;
                let echo = self.echo_buffer[i];
                let error = input - echo;
                let power = input * input + 1e-6;
                
                self.echo_buffer[i] += (MU / power) * error * input;
                *sample = error;
            }
        }
    }

    fn normalize_gain(&mut self, buffer: &mut [f32]) {
        const TARGET_LEVEL: f32 = 0.8;
        let mut peak = 0.0f32;

        for sample in buffer.iter() {
            peak = peak.max(sample.abs());
        }

        if peak > 0.001 {
            let gain = TARGET_LEVEL / peak;
            for sample in buffer.iter_mut() {
                *sample *= gain;
            }
        }
        self.peak_level = peak;
    }

    pub fn get_peak_level(&self) -> f32 {
        self.peak_level
    }
}
