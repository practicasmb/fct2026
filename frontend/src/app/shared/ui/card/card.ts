import { ChangeDetectionStrategy, Component, input, computed } from '@angular/core';

@Component({
  selector: 'ui-card',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div [class]="classes()"><ng-content /></div>`,
})
export class CardComponent {
  class = input<string>('');
  classes = computed(() => ['rounded-lg border bg-card text-card-foreground shadow-sm', this.class()].filter(Boolean).join(' '));
}

@Component({
  selector: 'ui-card-header',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div [class]="classes()"><ng-content /></div>`,
})
export class CardHeaderComponent {
  class = input<string>('');
  classes = computed(() => ['flex flex-col space-y-1.5 p-6', this.class()].filter(Boolean).join(' '));
}

@Component({
  selector: 'ui-card-title',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<h3 [class]="classes()"><ng-content /></h3>`,
})
export class CardTitleComponent {
  class = input<string>('');
  classes = computed(() => ['text-2xl font-semibold leading-none tracking-tight', this.class()].filter(Boolean).join(' '));
}

@Component({
  selector: 'ui-card-description',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<p [class]="classes()"><ng-content /></p>`,
})
export class CardDescriptionComponent {
  class = input<string>('');
  classes = computed(() => ['text-sm text-muted-foreground', this.class()].filter(Boolean).join(' '));
}

@Component({
  selector: 'ui-card-content',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div [class]="classes()"><ng-content /></div>`,
})
export class CardContentComponent {
  class = input<string>('');
  classes = computed(() => ['p-6 pt-0', this.class()].filter(Boolean).join(' '));
}

@Component({
  selector: 'ui-card-footer',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div [class]="classes()"><ng-content /></div>`,
})
export class CardFooterComponent {
  class = input<string>('');
  classes = computed(() => ['flex items-center p-6 pt-0', this.class()].filter(Boolean).join(' '));
}
