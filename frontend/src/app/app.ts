import { ChangeDetectionStrategy, Component, signal } from '@angular/core';
import { RouterOutlet, RouterLink, Router } from '@angular/router';
import { ButtonComponent, DialogComponent, BadgeComponent, CheckboxComponent } from '@shared/ui';
import type { DialogVariant, DialogSize } from '@shared/ui';

@Component({
  selector: 'app-root',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [RouterOutlet, ButtonComponent ],
  templateUrl: './app.html',
})
export class AppComponent {
  constructor(private readonly router: Router) {}
  readonly dialogVisible = signal(false);
  readonly dialogVariant = signal<DialogVariant>('default');
  readonly dialogSize    = signal<DialogSize>('default');

  openDialog(variant: DialogVariant, size: DialogSize = 'default'): void {
    this.dialogVariant.set(variant);
    this.dialogSize.set(size);
    this.dialogVisible.set(true);
  }
  goToTerms(): void {
    this.router.navigate(['/legal/terms']);
  }
}
