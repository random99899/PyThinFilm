export class AnimationController {
  constructor() {
    this.isPlaying = true;
    this.time = 0;
    this.speed = 1.0;
  }

  togglePlayPause() {
    this.isPlaying = !this.isPlaying;
    return this.isPlaying;
  }

  update(deltaSeconds) {
    if (this.isPlaying) {
      this.time += deltaSeconds * this.speed;
    }
    return this.time;
  }

  reset() {
    this.time = 0;
    this.isPlaying = true;
  }
}
